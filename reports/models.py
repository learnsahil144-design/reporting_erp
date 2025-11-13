from django.contrib.auth.models import AbstractUser
from django.db import models


# ------------------------------
# ✅ Custom User Model
# ------------------------------
class User(AbstractUser):
    TEAM_CHOICES = [
        ('content_writer', 'Content Writer'),
        ('graphic_designer', 'Graphic Designer'),
        ('video_editor', 'Video Editor'),
        ('social_media', 'Social Media'),
        ('video_producer', 'Video Producer'),
        ('reporter', 'Reporter'),
        ('cameraman', 'Cameraman'),
        ('marketing', 'Marketing'),
    ]
    team = models.CharField(max_length=50, choices=TEAM_CHOICES)
    contact = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


# ------------------------------
# ✅ Report Model
# ------------------------------
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
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='9_5_30')
    date = models.DateField(auto_now_add=True, help_text="Auto submission date")
    custom_date = models.DateField(blank=True, null=True, help_text="The date this report is for")

    # ✅ Static task fields (common or known ones)
    presenter_video = models.IntegerField(default=0, blank=True, null=True)
    live_video = models.IntegerField(default=0, blank=True, null=True)
    logo_video = models.IntegerField(default=0, blank=True, null=True)
    special_work_video = models.IntegerField(default=0, blank=True, null=True)
    reel_video = models.IntegerField(default=0, blank=True, null=True)
    vo_video = models.IntegerField(default=0, blank=True, null=True)
    interview_video = models.IntegerField(default=0, blank=True, null=True)
    anchor_presenter_video = models.IntegerField(default=0, blank=True, null=True)

    # ✅ Common notes field
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Keep dynamic fields as JSON too (optional)
    tasks = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.custom_date or self.date} ({self.get_shift_display()})"

    @property
    def is_late_submission(self):
        if self.custom_date:
            return self.custom_date < self.date
        return False


# ------------------------------
# ✅ Admin Notice Model
# ------------------------------
class AdminNotice(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ------------------------------
# ✅ Dynamic Field (for extra fields per team)
# ------------------------------
class DynamicField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('textarea', 'Textarea'),
        ('boolean', 'Checkbox'),
    ]

    TEAM_CHOICES = User.TEAM_CHOICES

    team = models.CharField(max_length=100, choices=TEAM_CHOICES)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=150)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team} - {self.label}"


# ------------------------------
# ✅ Dynamic Field Response (Stores the user input)
# ------------------------------
class DynamicFieldResponse(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='dynamic_responses')
    field = models.ForeignKey(DynamicField, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.field.label}: {self.value}"
