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
# 📝 USER REPORT SUBMISSION (with dynamic fields)
# ----------------------------------------------------
@login_required
def submit_report(request):
    user = request.user

    if request.method == "POST":
        form = ReportForm(request.POST, user=user)
        if form.is_valid():
            try:
                report = form.save()

                # ✅ Save dynamic field responses separately
                dynamic_fields = DynamicField.objects.filter(team=user.team)
                for field in dynamic_fields:
                    value = request.POST.get(field.name)
                    if value:
                        DynamicFieldResponse.objects.create(
                            report=report,
                            field=field,
                            value=value
                        )

                messages.success(request, "Report submitted successfully!")
                return redirect("submit_report")

            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReportForm(user=user)

    # ✅ Fetch dynamic fields for this user's team
    dynamic_fields = DynamicField.objects.filter(team=user.team)

    # ✅ Fetch notices and submission dates
    notices = AdminNotice.objects.all().order_by("-created_at")
    reports = Report.objects.filter(user=user)
    submission_dates = [r.custom_date.strftime("%Y-%m-%d") for r in reports if r.custom_date]

    context = {
        "form": form,
        "dynamic_fields": dynamic_fields,  # only rendered under “Additional Fields”
        "notices": notices,
        "submission_dates": json.dumps(submission_dates),
    }

    return render(request, "reports/submit_report.html", context)


# ----------------------------------------------------
# 🧭 ADMIN REPORT OVERVIEW
# ----------------------------------------------------
@staff_member_required
def admin_reports_overview(request):
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")
    date_filter = request.GET.get("date")

    reports = Report.objects.select_related("user").prefetch_related("dynamic_responses")

    if team_filter:
        reports = reports.filter(user__team=team_filter)
    if user_filter:
        reports = reports.filter(user__username=user_filter)
    if date_filter:
        reports = reports.filter(custom_date=date_filter)

    combined_reports = {}

    for r in reports:
        key = (r.user.id, r.custom_date or r.date, r.shift)
        if key not in combined_reports:
            combined_reports[key] = {
                "user": r.user,
                "team": r.user.team,
                "shift": r.get_shift_display(),
                "custom_date": r.custom_date or r.date,
                "created_at": r.created_at,
                "tasks": defaultdict(int),
                "notes": [],
                "is_late_submission": r.is_late_submission,
            }

        # ✅ Include static fields
        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
            except (TypeError, ValueError):
                combined_reports[key]["tasks"][k] = v

        # ✅ Include dynamic fields
        for response in r.dynamic_responses.all():
            combined_reports[key]["tasks"][response.field.label] = response.value

        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    # ✅ Format for display
    for key in combined_reports:
        formatted = {}
        for k, v in combined_reports[key]["tasks"].items():
            formatted[k.replace("_", " ").title()] = v
        combined_reports[key]["tasks"] = formatted

    combined_reports = list(combined_reports.values())

    # ✅ Stats
    reports_by_team = (
        reports.values("user__team")
        .distinct()
        .annotate(total=Count("custom_date"))
        .order_by("-total")
    )
    reports_by_user = (
        reports.values("user__username")
        .distinct()
        .annotate(total=Count("custom_date"))
        .order_by("-total")
    )

    teams = User.objects.values_list("team", flat=True).distinct()
    users = User.objects.all()

    return render(
        request,
        "reports/admin_overview.html",
        {
            "reports": combined_reports,
            "reports_by_team": reports_by_team,
            "reports_by_user": reports_by_user,
            "teams": teams,
            "users": users,
            "selected_team": team_filter,
            "selected_user": user_filter,
        },
    )


# ----------------------------------------------------
# 📦 EXPORT REPORTS TO EXCEL
# ----------------------------------------------------
@staff_member_required
def export_reports_excel(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")

    reports = Report.objects.select_related("user").prefetch_related("dynamic_responses")

    if start_date and end_date:
        reports = reports.filter(custom_date__range=[start_date, end_date])
    if team_filter:
        reports = reports.filter(user__team=team_filter)
    if user_filter:
        reports = reports.filter(user__username=user_filter)

    combined_reports = {}

    for r in reports:
        key = (r.user.id, r.custom_date or r.date, r.shift)
        if key not in combined_reports:
            combined_reports[key] = {
                "username": r.user.username,
                "team": r.user.team,
                "custom_date": r.custom_date or r.date,
                "shift": r.get_shift_display(),
                "tasks": defaultdict(int),
                "notes": [],
            }

        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
            except (TypeError, ValueError):
                combined_reports[key]["tasks"][k] = v

        for response in r.dynamic_responses.all():
            combined_reports[key]["tasks"][response.field.label] = response.value

        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    export_data = []
    for rep in combined_reports.values():
        data = {
            "username": rep["username"],
            "team": rep["team"],
            "custom_date": rep["custom_date"],
            "shift": rep["shift"],
            "notes": " | ".join(rep["notes"]),
        }
        data.update(rep["tasks"])
        export_data.append(data)

    df = pd.DataFrame(export_data)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="reports.xlsx"'
    df.to_excel(response, index=False)
    return response


# ----------------------------------------------------
# 👤 USER REPORT DETAIL
# ----------------------------------------------------
@staff_member_required
def user_report_detail(request, username):
    user = get_object_or_404(User, username=username)
    reports = Report.objects.filter(user=user).prefetch_related("dynamic_responses").order_by("custom_date")

    combined_reports = {}
    task_totals = defaultdict(int)
    daily_summary = defaultdict(int)
    monthly_summary = defaultdict(int)
    yearly_summary = defaultdict(int)

    for r in reports:
        date_key = r.custom_date or r.date
        key = (date_key, r.shift)
        if key not in combined_reports:
            combined_reports[key] = {
                "custom_date": date_key,
                "shift": r.get_shift_display(),
                "tasks": defaultdict(int),
                "notes": [],
                "is_late_submission": r.is_late_submission,
            }

        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
                task_totals[k] += int(v)
                daily_summary[date_key] += int(v)
                if r.custom_date:
                    month = r.custom_date.strftime("%b %Y")
                    year = r.custom_date.year
                    monthly_summary[month] += int(v)
                    yearly_summary[year] += int(v)
            except (TypeError, ValueError):
                continue

        for response in r.dynamic_responses.all():
            combined_reports[key]["tasks"][response.field.label] = response.value

        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    for key in combined_reports:
        formatted = {}
        for k, v in combined_reports[key]["tasks"].items():
            formatted[k.replace("_", " ").title()] = v
        combined_reports[key]["tasks"] = formatted

    context = {
        "user": user,
        "reports": list(combined_reports.values()),
        "task_totals": dict((k.replace("_", " ").title(), v) for k, v in task_totals.items()),
        "daily_summary": {str(k): v for k, v in sorted(daily_summary.items())},
        "monthly_summary": dict(monthly_summary),
        "yearly_summary": dict(yearly_summary),
    }

    return render(request, "reports/user_detail.html", context)
