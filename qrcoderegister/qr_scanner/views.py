from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
@login_required
def scan_qr(request):
    return render(request, 'scan_qr.html')






