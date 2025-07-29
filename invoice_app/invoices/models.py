from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    upload_time = models.DateTimeField(default=timezone.now)
    original_file_name = models.CharField(max_length=255, default="unknown")
    company_name = models.CharField(max_length=20, default="")
    invoice_number = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
class UploadFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class RejectedFile(models.Model):
    file = models.FileField(upload_to='failed_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True) 

class Log(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', 'File Uploaded'),
        ('SCAN_SUCCESS', 'Scan Successful'),
        ('SCAN_FAILED', 'Scan Failed'),
        ('DELETE', 'File Deleted'),
        ('LOGIN', 'User Logged In'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)