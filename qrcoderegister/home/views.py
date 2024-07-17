from os import error
from django.shortcuts import render , redirect
from requests_toolbelt import user_agent
from . forms import SignUpForm,Add
from django.contrib.auth import login,logout
import random
import string
import qrcode
from io import BytesIO
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
from openpyxl import Workbook
import json
from . models import Attendance
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.contrib import messages
from django.contrib.auth.models import User
import pandas as pd


def frontpage(request):
    return render(request,template_name='frontpage.html')

def signup(request):
    
    if request.method=='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            return redirect('frontpage')
         
    else:
        form=SignUpForm()
    return render(request,'signup.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('/')

# def autocomplete(request):
#     if 'term' in request.GET:
#         qs = Attendance.objects.filter(user__icontains=request.GET.get('term'))
#         names = list(qs.values_list('user', flat=True))
#         return JsonResponse(names, safe=False)
#     return JsonResponse([], safe=False)

def generate_random_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))



def register(request):
    if request.method == 'POST':
        form = Add(request.POST)
        
        if form.is_valid():
            attendance=form.save(commit=False)
            attendance.ip = None
            attendance.save()
            messages.success(request,'Attendance marked successfully.')
        else:
            messages.warning(request,'Error marking attendance.')        
    else:
        form = Add()

    attendees = Attendance.objects.all().order_by('-timestamp')
    context = {
        'form': form,
        'timestamp': timezone.now(),
        'attendees': attendees,
    }
    return render(request, 'register2.html', context)


def serve_qr_code(request):
    random_code = generate_random_code()
    img = qrcode.make(random_code)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@csrf_exempt
def poll_view(request):
    if request.method == 'POST':
        # Update the server state
        request.session['trigger'] = True
        return JsonResponse({'status': 'triggered'})
    else:
        trigger = request.session.get('trigger', False)
        if trigger:
            request.session['trigger'] = False
            return JsonResponse({'trigger': True})
        return JsonResponse({'trigger': False})



@csrf_exempt
@require_http_methods(["POST"])
def validate_attendance(request):
    data = json.loads(request.body.decode('utf-8'))
    qr_code = data.get('qr_code')
    print(qr_code)
    ip = data.get('ip')
    print(ip)

    # Check if both qr_code and ip are present
    if qr_code is None or ip is None:
        return JsonResponse({'success': False, 'error': 'Missing QR code or IP data'})

    # Proceed with attendance check
    today = timezone.now().date()
    attendance = Attendance.objects.filter(user=request.user, timestamp__date=today, ip=ip).first()
    if attendance:
        return JsonResponse({'success': False, 'error': 'Attendance already registered for today'})
    if Attendance.objects.filter(ip=ip).exists():
        return JsonResponse({'success': False, 'error': 'This device has already been used for today'})
    if Attendance.objects.filter(random_code = qr_code).exists():
        return JsonResponse({'success': False,'error': 'QR code has arleady been scanned'})
    else:
        Attendance.objects.create(user=request.user, timestamp=timezone.now(), ip=ip,random_code = qr_code)
        return JsonResponse({'success': True})

def export_to_excel(request):
    wb = Workbook()
    ws = wb.active
    
    # Add header row
    headers = ['Username', 'Timestamp']  # Adjust headers as needed
    ws.append(headers)
    
    # Fetch data from your model
    data = Attendance.objects.all()
    
    # Add data to the worksheet
    for item in data:
        ws.append([
            item.user.username,  # Use username instead of User object
            item.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as string
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export.xlsx'
    
    wb.save(response)
    
    return response


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            for index, row in df.iterrows():
                user, created = User.objects.get_or_create(
                    username=row['username'],
                    defaults={
                        'first_name': row['name'],
                        'email': row['phone']
                    }
                )
                if created:
                    user.set_password(row['username'])
                    user.save()
                else:
                    messages.warning(request, f'User {row["username"]} already exists.')

            messages.success(request, 'Successfully imported users from Excel file.')
            return redirect('upload_file')
    else:
        form = UploadFileForm()
    return render(request, 'upload2.html', {'form': form})



def attendance_stats(request):
    # Get all users
    all_users = User.objects.filter(is_superuser=False)
    # Get all users marked present
    present_users = User.objects.filter(attendance__isnull=False)
    
    # Calculate absent users
    absent_users = all_users.exclude(id__in=present_users)
    
    # Calculate statistics
    total_users = all_users.count()
    present_count = present_users.count()
    absent_count = absent_users.count()
    
    attendance_rate = (present_count / total_users) * 100 if total_users > 0 else 0
    
    context = {
        'total_users': total_users,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': round(attendance_rate, 2),
        'absent_users': absent_users,
    }
    
    return render(request, 'attendance_stats.html', context)


