from django import forms
from .models import Report, User


class ReportForm(forms.ModelForm):
    custom_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Add extra notes..."}),
        label="Notes"
    )

    shift = forms.ChoiceField(
        choices=Report.SHIFT_CHOICES,
        label="Shift Timing",
        required=True
    )

    class Meta:
        model = Report
        fields = ["custom_date", "shift", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ✅ Add default static fields based on the user's team
        if not self.user:
            return

        team = self.user.team

        # ---------------------- Video Producer ----------------------
        if team == "video_producer":
            static_fields = [
                "Presenter Video", "Live Video", "Logo Video", "Special Work Video",
                "Reel Video", "VO Video", "Interview Video", "Anchor/Presenter Video"
            ]

        # ---------------------- Video Editor ----------------------
        elif team == "video_editor":
            static_fields = [
                "Logo Video", "Reel Video", "Two/Three Frame Video", "VO Video",
                "Presenter Video", "Khabarbaat Video", "Special Interview",
                "Video Shoot", "इतर"
            ]

        # ---------------------- Graphics Designer ----------------------
        elif team == "graphic_designer":
            static_fields = [
                "Thumbnail (IG/YT)", "Reel/Live Thumbnail", "WhatsApp Creative",
                "News of the Day", "News/Vdo Comment Link", "Infographics", "Slider",
                "Statement", "Special Day", "Swipe Up", "Pointer Creative",
                "Special Video Graphics", "Comment Creative"
            ]

        # ---------------------- Content Writer ----------------------
        elif team == "content_writer":
            static_fields = [
                "News", "Bulletin", "Gallery", "Web Story", "Creative",
                "Slider", "X Post", "App Post"
            ]

        # ---------------------- Social Media ----------------------
        elif team == "social_media":
            static_fields = [
                "Video Post", "Creative Post", "Live Video", "Slider Post",
                "Swipe Up", "News In Comment", "Paid Promotion Post"
            ]

        # ---------------------- Reporter ----------------------
        elif team == "reporter":
            static_fields = [
                "Attended Press Conference", "Breaking News", "Special Story", "Interview"
            ]

        # ---------------------- Cameraman ----------------------
        elif team == "cameraman":
            static_fields = [
                "Attended Press Conference", "Special Story", "Interview",
                "Event", "B Rolls", "Live"
            ]

        # ---------------------- Marketing ----------------------
        elif team == "marketing":
            static_fields = [
                "Client Visit Details", "Next Day Plan", "Client Follow-up Details"
            ]

        else:
            static_fields = []

        # Dynamically create form fields for each static field
        for label in static_fields:
            field_name = label.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            self.fields[field_name] = forms.IntegerField(
                min_value=0, initial=0, required=False, label=label
            )

    def save(self, commit=True):
        report = super().save(commit=False)
        report.user = self.user

        # ✅ Collect all numeric/static fields into JSON
        tasks_data = {
            k: v for k, v in self.cleaned_data.items()
            if k not in ["custom_date", "notes", "shift"]
        }
        report.tasks = tasks_data
        report.shift = self.cleaned_data.get("shift")
        report.notes = self.cleaned_data.get("notes", "")

        if commit:
            report.save()
        return report


# ✅ Admin filter form for filtering reports
class ReportFilterForm(forms.Form):
    team = forms.ChoiceField(
        choices=[("", "All Teams")] + list(User.TEAM_CHOICES),
        required=False,
        label="Select Team"
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Select User"
    )
    shift = forms.ChoiceField(
        choices=[("", "All Shifts")] + list(Report.SHIFT_CHOICES),
        required=False,
        label="Select Shift"
    )
