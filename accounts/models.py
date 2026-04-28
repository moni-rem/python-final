from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class PlatformConfiguration(models.Model):
    site_title = models.CharField(max_length=255, default='Online Learning Platform')
    site_description = models.TextField(blank=True, null=True)
    support_email = models.EmailField(blank=True, null=True)
    support_phone = models.CharField(max_length=50, blank=True, null=True)
    terms_of_service_url = models.URLField(blank=True, null=True)
    privacy_policy_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = 'Platform Configuration'
        verbose_name_plural = 'Platform Configurations'

    def __str__(self):
        return self.site_title
