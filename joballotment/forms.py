from django import forms
from .models import Job, Report, CustomUser
from django.contrib.auth.forms import UserCreationForm

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'assigned_to', 'supervisor']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']

class JobAllotmentForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['assigned_to', 'supervisor']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content'] 