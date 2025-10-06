from django import forms
from .models import Report, User   # ✅ ensure User is imported


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

    shift = forms.ChoiceField(   # ✅ new shift field
        choices=Report.SHIFT_CHOICES,
        label="Shift Timing",
        required=True
    )

    class Meta:
        model = Report
        fields = ["custom_date", "shift", "notes"]

    def __init__(self, *args, **kwargs):
        # Expect the current user to be passed as `user=...`
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Add team-specific task fields dynamically
        if self.user:
            if self.user.team == "content_writer":
                self.fields["short_video"] = forms.IntegerField(min_value=0, initial=0, label="Short Videos")
                self.fields["reels"] = forms.IntegerField(min_value=0, initial=0, label="Reels")
                self.fields["long_video"] = forms.IntegerField(min_value=0, initial=0, label="Long Videos")
                self.fields["interview"] = forms.IntegerField(min_value=0, initial=0, label="Interviews")

            elif self.user.team == "graphic_designer":
                self.fields["reel_thumbnail"] = forms.IntegerField(min_value=0, initial=0, label="Reel Thumbnails")
                self.fields["interview_thumbnail"] = forms.IntegerField(min_value=0, initial=0, label="Interview Thumbnails")
                self.fields["short_thumbnail"] = forms.IntegerField(min_value=0, initial=0, label="Short Thumbnails")
                self.fields["post"] = forms.IntegerField(min_value=0, initial=0, label="Social Media Posts")
                self.fields["scroller"] = forms.IntegerField(min_value=0, initial=0, label="Scrollers")

            elif self.user.team == "video_editor":
                self.fields["edit_short_video"] = forms.IntegerField(min_value=0, initial=0, label="Edited Short Videos")
                self.fields["edit_reels"] = forms.IntegerField(min_value=0, initial=0, label="Edited Reels")
                self.fields["edit_long_video"] = forms.IntegerField(min_value=0, initial=0, label="Edited Long Videos")
                self.fields["edit_interview"] = forms.IntegerField(min_value=0, initial=0, label="Edited Interviews")

            elif self.user.team == "social_media":
                self.fields["facebook_posts"] = forms.IntegerField(min_value=0, initial=0, label="Facebook Posts")
                self.fields["instagram_posts"] = forms.IntegerField(min_value=0, initial=0, label="Instagram Posts")
                self.fields["youtube_posts"] = forms.IntegerField(min_value=0, initial=0, label="YouTube Posts")

    def save(self, commit=True):
        report = super().save(commit=False)
        report.user = self.user

        # Collect all dynamic task fields into JSON
        tasks_data = {
            k: v for k, v in self.cleaned_data.items()
            if k not in ["custom_date", "notes", "shift"]
        }
        report.tasks = tasks_data

        # ✅ Save shift and notes
        report.shift = self.cleaned_data.get("shift")
        report.notes = self.cleaned_data.get("notes", "")

        if commit:
            report.save()
        return report


# ✅ Admin filter form
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
    shift = forms.ChoiceField(   # ✅ new filter by shift
        choices=[("", "All Shifts")] + list(Report.SHIFT_CHOICES),
        required=False,
        label="Select Shift"
    )
