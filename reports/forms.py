from django import forms
from .models import Report, User


class ReportForm(forms.ModelForm):
    custom_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        )
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Add extra notes...",
                "class": "form-control",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        ),
        label="Notes"
    )

    shift = forms.ChoiceField(
        choices=Report.SHIFT_CHOICES,
        label="Shift Timing",
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        )
    )

    class Meta:
        model = Report
        fields = ["custom_date", "shift", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ----------------- Add Bootstrap to default fields ---------------------
        for field in self.fields.values():
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"
            field.widget.attrs.setdefault("style", "border-radius:8px; padding:8px 10px;")

        # ----------------- No user? No dynamic fields --------------------------
        if not self.user:
            return

        team = self.user.team

        # --------------------- TEAM STATIC FIELDS ------------------------------
        TEAM_FIELDS = {
            "video_producer": [
                "Presenter Video", "Live Video", "Logo Video", "Special Work Video",
                "Reel Video", "VO Video", "Interview Video", "Anchor/Presenter Video"
            ],
            "video_editor": [
                "Logo Video", "Reel Video", "Two/Three Frame Video", "VO Video",
                "Presenter Video", "Khabarbaat Video", "Special Interview",
                "Video Shoot", "इतर"
            ],
            "graphic_designer": [
                "Thumbnail (IG/YT)", "Reel/Live Thumbnail", "WhatsApp Creative",
                "News of the Day", "News/Vdo Comment Link", "Infographics", "Slider",
                "Statement", "Special Day", "Swipe Up", "Pointer Creative",
                "Special Video Graphics", "Comment Creative"
            ],
            "content_writer": [
                "News", "Bulletin", "Gallery", "Web Story", "Creative",
                "Slider", "X Post", "App Post"
            ],
            "social_media": [
                "Video Post", "Creative Post", "Live Video", "Slider Post",
                "Swipe Up", "News In Comment", "Paid Promotion Post"
            ],
            "reporter": [
                "Attended Press Conference", "Breaking News",
                "Special Story", "Interview"
            ],
            "cameraman": [
                "Attended Press Conference", "Special Story",
                "Interview", "Event", "B Rolls", "Live"
            ],
            "marketing": [
                "Client Visit Details", "Next Day Plan", "Client Follow-up Details"
            ],
        }

        static_fields = TEAM_FIELDS.get(team, [])

        # ------------------ Create dynamic numeric fields -----------------------
        for label in static_fields:
            field_name = label.lower().replace(" ", "_").replace("/", "_").replace("-", "_")

            self.fields[field_name] = forms.IntegerField(
                min_value=0,
                initial=0,
                required=False,
                label=label,
                widget=forms.NumberInput(
                    attrs={
                        "class": "form-control",
                        "style": "border-radius:8px; padding:8px 10px;"
                    }
                )
            )

    def save(self, commit=True):
        report = super().save(commit=False)
        report.user = self.user

        # Collect all dynamic fields except main fields
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


# ---------------- Admin Filter Form -------------------
class ReportFilterForm(forms.Form):
    team = forms.ChoiceField(
        choices=[("", "All Teams")] + list(User.TEAM_CHOICES),
        required=False,
        label="Select Team",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        )
    )

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Select User",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        )
    )

    shift = forms.ChoiceField(
        choices=[("", "All Shifts")] + list(Report.SHIFT_CHOICES),
        required=False,
        label="Select Shift",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "style": "border-radius:8px; padding:8px 10px;"
            }
        )
    )
