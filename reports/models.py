from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    TEAM_CHOICES = [
        ('content_writer', 'Content Writer'),
        ('graphic_designer', 'Graphic Designer'),
        ('video_editor', 'Video Editor'),
        ('social_media', 'Social Media'),
    ]
    team = models.CharField(max_length=50, choices=TEAM_CHOICES)
    contact = models.CharField(max_length=15, blank=True, null=True)

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    custom_date = models.DateField(blank=True, null=True)
    tasks = models.JSONField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
