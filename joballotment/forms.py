from django import forms
from .models import Job, Report, CustomUser
from django.contrib.auth.forms import UserCreationForm

JOB_TITLE_CHOICES = [
    ('', 'Select a job title'),
    ('Computer', 'Computer'),
    ('Printer', 'Printer'),
    ('Network', 'Network'),
    ('Camera', 'Camera'),
    ('Mail', 'Mail'),
    ('Antivirus', 'Antivirus'),
    ('SAP', 'SAP'),
    ('MCS', 'MCS'),
    ('Other', 'Other'),
]

class JobForm(forms.ModelForm):
    job_title_dropdown = forms.ChoiceField(choices=JOB_TITLE_CHOICES, required=False, label='Job Title (select)')
    class Meta:
        model = Job
        fields = ['title', 'job_title_dropdown', 'description', 'assigned_to', 'supervisor', 'remark']

    def clean(self):
        cleaned_data = super().clean()
        dropdown = cleaned_data.get('job_title_dropdown')
        title = cleaned_data.get('title')
        if dropdown and dropdown != 'Other' and dropdown != '':
            cleaned_data['title'] = dropdown
        elif not title:
            raise forms.ValidationError('Please provide a job title.')
        return cleaned_data

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