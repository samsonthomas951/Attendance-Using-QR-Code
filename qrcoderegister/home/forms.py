from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from . models import Attendance
from django import forms
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username','email','password1','password2']    


class Add(forms.ModelForm):
    user = forms.CharField(widget=forms.TextInput(attrs={'class': 'otp-input', 'placeholder': 'Enter username here..'}))

    class Meta:
        model = Attendance
        fields = ['user']
        widgets = {
       'name': forms.TextInput(attrs={'class': 'otp-input', 'placeholder': 'Enter username here..'}),
    }
        
    # def clean_user(self):
    #     username = self.cleaned_data['user']
    #     try:
    #         user = User.objects.get(username=username)
    #         attendance = Attendance.get(user=username)
    #     except User.DoesNotExist and Attendance.:
    #         raise forms.ValidationError("User does not exist.")
    #     return user
    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")

        # Check if attendance has already been marked for this user
        if Attendance.objects.filter(user=user).exists():
            raise forms.ValidationError("Attendance has already been marked for this user.")

        return user

    
class UploadFileForm(forms.Form):
    file = forms.FileField()