from django.db import models

# Create your models here.

from django.db import models

class SuperMentor(models.Model):
    # Add these choices at the top of the class
    DESIGNATION_CHOICES = [
        ('mentor', 'Mentor'),
        ('super_mentor', 'Super Mentor'),
    ]
    
    name = models.CharField(max_length=100)
    expertise = models.CharField(max_length=200)
    bio = models.TextField()
    photo = models.ImageField(upload_to='super_mentors/')
    
    # Add this new field
    designation = models.CharField(
        max_length=20,
        choices=DESIGNATION_CHOICES,
        default='mentor'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Mentor & Super Mentor"
        verbose_name_plural = "Mentor & Super Mentor"
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        # FIX: Safe access to user.email - check if user exists first
        if self.user and self.user.email:
            return f"{self.user.email} - {self.otp}"
        elif self.email:  # Use the email field directly if user is None
            return f"{self.email} - {self.otp}"
        elif self.username:  # Use username if available
            return f"{self.username} - {self.otp}"
        else:
            return f"OTP: {self.otp}"