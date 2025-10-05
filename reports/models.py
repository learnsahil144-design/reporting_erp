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
    
    # ✅ Auto date (when submitted)
    date = models.DateField(auto_now_add=True, help_text="Auto submission date")
    
    # ✅ Custom date (optional, if user missed the actual day)
    custom_date = models.DateField(blank=True, null=True, help_text="The date this report is for")
    
    tasks = models.JSONField()
    notes = models.TextField(blank=True, null=True)
    
    # ✅ Exact timestamp (more precise than 'date')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.custom_date or self.date}"

    @property
    def is_late_submission(self):
        """Check if user submitted report for a past date"""
        if self.custom_date:
            return self.custom_date < self.date
        return False

