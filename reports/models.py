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
    SHIFT_CHOICES = [
        ('7_3_30', '7:00 AM – 3:30 PM'),
        ('8_8_30', '8:00 AM – 8:30 PM'),
        ('9_5_30', '9:00 AM – 5:30 PM'),
        ('10_6_30', '10:00 AM – 6:30 PM'),
        ('12_8_30', '12:00 PM – 8:30 PM'),
        ('2_30_11', '2:30 PM – 11:00 PM'),
        ('wfh', 'Work From Home'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # ✅ Shift selection
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='9_5_30')

    # ✅ Dates
    date = models.DateField(auto_now_add=True, help_text="Auto submission date")
    custom_date = models.DateField(blank=True, null=True, help_text="The date this report is for")
    
    # ✅ Task and notes
    tasks = models.JSONField()
    notes = models.TextField(blank=True, null=True)
    
    # ✅ Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.custom_date or self.date} ({self.get_shift_display()})"

    @property
    def is_late_submission(self):
        """Check if user submitted report for a past date"""
        if self.custom_date:
            return self.custom_date < self.date
        return False
