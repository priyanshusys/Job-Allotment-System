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

DEPARTMENT_CODE_CHOICES = [
    ('', 'Select Department'),
    ('HR', 'HR'),
    ('IT', 'IT'),
    ('FIN', 'FIN'),
    ('MKT', 'MKT'),
]

DESIGNATION_CHOICES = [
    ('', 'Select Designation'),
    ('Manager', 'Manager'),
    ('Executive', 'Executive'),
    ('Staff', 'Staff'),
]

class CustomUserCreationForm(UserCreationForm):
    department_code = forms.ChoiceField(choices=DEPARTMENT_CODE_CHOICES, required=False)
    designation = forms.ChoiceField(choices=DESIGNATION_CHOICES, required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'department_code', 'department_name', 'designation', 'password1', 'password2']
        # user_id is excluded on purpose

class JobAllotmentForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['assigned_to', 'supervisor']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content']

class NewTitleForm(forms.Form):
    title_name = forms.CharField(label='Title Name', max_length=255, required=True)
    title_code = forms.CharField(label='Title Code', max_length=50, required=True) 