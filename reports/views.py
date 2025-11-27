from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from collections import defaultdict
import pandas as pd
import json

from .forms import ReportForm
from .models import Report, User, AdminNotice, DynamicField, DynamicFieldResponse


# ----------------------------------------------------
# 📝 USER REPORT SUBMISSION (supports static + dynamic fields)
# ----------------------------------------------------
@login_required
def submit_report(request):
    user = request.user

    if request.method == "POST":
        form = ReportForm(request.POST, user=user)

        if form.is_valid():
            try:
                report = form.save()

                # Save dynamic fields for user’s team
                dynamic_fields = DynamicField.objects.filter(team=user.team)
                for field in dynamic_fields:
                    value = request.POST.get(field.name)
                    if value:
                        DynamicFieldResponse.objects.create(
                            report=report,
                            field=field,
                            value=value,
                        )

                messages.success(request, "Report submitted successfully!")
                return redirect("submit_report")

            except ValidationError as e:
                messages.error(request, str(e))

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ReportForm(user=user)

    # Fetch dynamic fields for template
    dynamic_fields = DynamicField.objects.filter(team=user.team)

    # Calendar highlight
    reports = Report.objects.filter(user=user)
    submission_dates = [
        r.custom_date.strftime("%Y-%m-%d")
        for r in reports
        if r.custom_date
    ]

    context = {
        "form": form,
        "dynamic_fields": dynamic_fields,
        "notices": AdminNotice.objects.all().order_by("-created_at"),
        "submission_dates": json.dumps(submission_dates),
    }

    return render(request, "reports/submit_report.html", context)


# ----------------------------------------------------
# 👁 USER REPORT PREVIEW (Fix applied)
# ----------------------------------------------------
@login_required
def user_report_preview(request, date):
    """
    Show report preview (static + dynamic fields)
    for the authenticated user.
    """
    report = (
        Report.objects
        .filter(user=request.user, custom_date=date)
        .prefetch_related("dynamic_responses")
        .first()
    )

    if not report:
        messages.error(request, f"No report found for {date}.")
        return redirect("submit_report")

    # STATIC FIELDS (from Report.tasks JSON)
    static_fields = {
        k.replace("_", " ").title(): v
        for k, v in (report.tasks or {}).items()
    }

    # DYNAMIC FIELDS (from DynamicFieldResponse)
    dynamic_fields = {
        resp.field.label: resp.value
        for resp in report.dynamic_responses.all()
    }

    return render(
        request,
        "reports/user_report_preview.html",
        {
            "report": report,
            "static_fields": static_fields,
            "dynamic_fields": dynamic_fields,
            "selected_date": date,
        }
    )


# ----------------------------------------------------
# 🧭 ADMIN REPORT OVERVIEW
# ----------------------------------------------------
@staff_member_required
def admin_reports_overview(request):
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")
    date_filter = request.GET.get("date")

    reports = Report.objects.select_related("user").prefetch_related("dynamic_responses")

    # Filters
    if team_filter:
        reports = reports.filter(user__team=team_filter)
    if user_filter:
        reports = reports.filter(user__username=user_filter)
    if date_filter:
        reports = reports.filter(custom_date=date_filter)

    combined = {}

    # Combine by (user, date, shift)
    for r in reports:
        key = (r.user.id, r.custom_date, r.shift)

        if key not in combined:
            combined[key] = {
                "user": r.user,
                "team": r.user.team,
                "shift": r.get_shift_display(),
                "custom_date": r.custom_date,
                "tasks": defaultdict(int),
                "notes": [],
                "created_at": r.created_at,
                "is_late_submission": r.is_late_submission,
            }

        # Static fields
        for k, v in (r.tasks or {}).items():
            try:
                combined[key]["tasks"][k] += int(v)
            except:
                combined[key]["tasks"][k] = v

        # Dynamic fields
        for resp in r.dynamic_responses.all():
            combined[key]["tasks"][resp.field.label] = resp.value

        if r.notes:
            combined[key]["notes"].append(r.notes)

    # Format for frontend
    for key in combined:
        formatted = {}
        for k, v in combined[key]["tasks"].items():
            formatted[k.replace("_", " ").title()] = v
        combined[key]["tasks"] = formatted

    return render(
        request,
        "reports/admin_overview.html",
        {
            "reports": list(combined.values()),
            "reports_by_team": reports.values("user__team").annotate(total=Count("id")),
            "reports_by_user": reports.values("user__username").annotate(total=Count("id")),
            "teams": User.objects.values_list("team", flat=True).distinct(),
            "users": User.objects.all(),
            "selected_team": team_filter,
            "selected_user": user_filter,
        },
    )


# ----------------------------------------------------
# 📦 EXPORT TO EXCEL
# ----------------------------------------------------
@staff_member_required
def export_reports_excel(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")

    reports = Report.objects.select_related("user").prefetch_related("dynamic_responses")

    # Filters
    if start_date and end_date:
        reports = reports.filter(custom_date__range=[start_date, end_date])
    if team_filter:
        reports = reports.filter(user__team=team_filter)
    if user_filter:
        reports = reports.filter(user__username=user_filter)

    combined = {}

    for r in reports:
        key = (r.user.id, r.custom_date, r.shift)

        if key not in combined:
            combined[key] = {
                "username": r.user.username,
                "team": r.user.team,
                "custom_date": r.custom_date,
                "shift": r.get_shift_display(),
                "tasks": defaultdict(int),
                "notes": [],
            }

        for k, v in (r.tasks or {}).items():
            try:
                combined[key]["tasks"][k] += int(v)
            except:
                combined[key]["tasks"][k] = v

        for resp in r.dynamic_responses.all():
            combined[key]["tasks"][resp.field.label] = resp.value

        if r.notes:
            combined[key]["notes"].append(r.notes)

    # Convert to dataframe
    export_data = []
    for rep in combined.values():
        row = {
            "username": rep["username"],
            "team": rep["team"],
            "custom_date": rep["custom_date"],
            "shift": rep["shift"],
            "notes": " | ".join(rep["notes"]),
        }
        row.update(rep["tasks"])
        export_data.append(row)

    df = pd.DataFrame(export_data)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="reports.xlsx"'
    df.to_excel(response, index=False)
    return response


# ----------------------------------------------------
# 👤 ADMIN: USER DETAIL PAGE
# ----------------------------------------------------
@staff_member_required
def user_report_detail(request, username):
    user = get_object_or_404(User, username=username)
    reports = (
        Report.objects.filter(user=user)
        .prefetch_related("dynamic_responses")
        .order_by("custom_date")
    )

    combined = {}
    task_totals = defaultdict(int)
    daily_summary = defaultdict(int)
    monthly_summary = defaultdict(int)
    yearly_summary = defaultdict(int)

    for r in reports:
        date_key = r.custom_date
        key = (date_key, r.shift)

        if key not in combined:
            combined[key] = {
                "custom_date": date_key,
                "shift": r.get_shift_display(),
                "tasks": defaultdict(int),
                "notes": [],
                "is_late_submission": r.is_late_submission,
            }

        # Static fields
        for k, v in (r.tasks or {}).items():
            try:
                combined[key]["tasks"][k] += int(v)
                task_totals[k] += int(v)
                daily_summary[date_key] += int(v)

                month = date_key.strftime("%b %Y")
                yearly = date_key.year

                monthly_summary[month] += int(v)
                yearly_summary[yearly] += int(v)

            except:
                continue

        # Dynamic fields
        for resp in r.dynamic_responses.all():
            combined[key]["tasks"][resp.field.label] = resp.value

        if r.notes:
            combined[key]["notes"].append(r.notes)

    # Format task names
    for key in combined:
        formatted = {
            k.replace("_", " ").title(): v
            for k, v in combined[key]["tasks"].items()
        }
        combined[key]["tasks"] = formatted

    context = {
        "user": user,
        "reports": list(combined.values()),
        "task_totals": {k.replace("_", " ").title(): v for k, v in task_totals.items()},
        "daily_summary": {str(k): v for k, v in sorted(daily_summary.items())},
        "monthly_summary": dict(monthly_summary),
        "yearly_summary": dict(yearly_summary),
    }

    return render(request, "reports/user_detail.html", context)
