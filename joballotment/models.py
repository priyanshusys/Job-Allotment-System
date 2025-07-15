from django.db import models
from django.contrib.auth.models import AbstractUser

# User roles
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('user', 'User'),
    ('supervisor', 'Supervisor'),
]

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    user_id = models.CharField(max_length=5, unique=True, blank=True, null=True)
    department_code = models.CharField(max_length=10, blank=True, null=True)
    department_name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.user_id:
            # Generate a unique 5-digit user_id
            import random
            while True:
                new_id = str(random.randint(10000, 99999))
                if not CustomUser.objects.filter(user_id=new_id).exists():
                    self.user_id = new_id
                    break
        super().save(*args, **kwargs)

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey('CustomUser', related_name='jobs', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'user'})
    supervisor = models.ForeignKey('CustomUser', related_name='supervised_jobs', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'supervisor'})
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('user', 'User'),
        ('supervisor', 'Supervisor'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    content = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('verified', 'Verified')], default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.report_type} report"
