from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from .forms import ReportForm
from .models import Report, User
from collections import defaultdict
import pandas as pd

# ------------------------------
# 📝 USER REPORT SUBMISSION
# ------------------------------
@login_required
def submit_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Report submitted successfully!")
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect("submit_report")
    else:
        form = ReportForm(user=request.user)
    return render(request, "reports/submit_report.html", {"form": form})


# ------------------------------
# 🖥️ ADMIN REPORT OVERVIEW
# ------------------------------
@staff_member_required
def admin_reports_overview(request):
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")
    date_filter = request.GET.get("date")

    reports = Report.objects.select_related("user").all()

    # ✅ Filtering
    if team_filter:
        reports = reports.filter(user__team=team_filter)
    if user_filter:
        reports = reports.filter(user__username=user_filter)
    if date_filter:
        reports = reports.filter(custom_date=date_filter)

    # ✅ Combine multiple reports per user per day per shift
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

        # Merge numeric tasks
        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
            except (TypeError, ValueError):
                pass

        # Combine notes
        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    # ✅ Format task keys
    for key in combined_reports:
        formatted_tasks = {}
        for k, v in combined_reports[key]["tasks"].items():
            formatted_key = k.replace("_", " ").title()
            formatted_tasks[formatted_key] = v
        combined_reports[key]["tasks"] = formatted_tasks

    combined_reports = list(combined_reports.values())

    # ✅ Aggregations for charts
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

    # ✅ Dropdown lists
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


# ------------------------------
# 📝 EXPORT REPORTS TO EXCEL (with date range support)
# ------------------------------
@staff_member_required
def export_reports_excel(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    team_filter = request.GET.get("team")
    user_filter = request.GET.get("user")

    reports = Report.objects.select_related("user").all()

    # Apply filters
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

        # Merge numeric tasks safely
        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
            except (TypeError, ValueError):
                combined_reports[key]["tasks"][k] = v

        # Combine notes
        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    # Flatten tasks and notes for Excel
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

# ------------------------------
# 👤 USER REPORT DETAIL (for admin dashboard)
# ------------------------------
@staff_member_required
def user_report_detail(request, username):
    user = get_object_or_404(User, username=username)

    reports = Report.objects.filter(user=user).order_by("custom_date")

    # Combine multiple reports per day per shift
    combined_reports = {}
    task_totals = defaultdict(int)  # ✅ Aggregate all tasks for graph

    for r in reports:
        key = (r.custom_date or r.date, r.shift)
        if key not in combined_reports:
            combined_reports[key] = {
                "custom_date": r.custom_date or r.date,
                "shift": r.get_shift_display(),
                "tasks": defaultdict(int),
                "notes": [],
                "is_late_submission": r.is_late_submission,
            }

        # Merge numeric tasks
        for k, v in (r.tasks or {}).items():
            try:
                combined_reports[key]["tasks"][k] += int(v)
                task_totals[k] += int(v)  # Add to total for graph
            except (TypeError, ValueError):
                combined_reports[key]["tasks"][k] = v

        # Combine notes
        if r.notes:
            combined_reports[key]["notes"].append(r.notes)

    # Format task keys for display
    for key in combined_reports:
        formatted_tasks = {}
        for k, v in combined_reports[key]["tasks"].items():
            formatted_key = k.replace("_", " ").title()
            formatted_tasks[formatted_key] = v
        combined_reports[key]["tasks"] = formatted_tasks

    combined_reports_list = list(combined_reports.values())

    # Monthly & yearly aggregation for charts
    monthly_summary = defaultdict(int)
    yearly_summary = defaultdict(int)
    for r in reports:
        if r.custom_date:
            month = r.custom_date.strftime("%b %Y")
            year = r.custom_date.year
            monthly_summary[month] += 1
            yearly_summary[year] += 1

    context = {
        "user": user,
        "reports": combined_reports_list,
        "monthly_summary": dict(monthly_summary),
        "yearly_summary": dict(yearly_summary),
        "task_totals": dict((k.replace("_", " ").title(), v) for k, v in task_totals.items()),  # ✅ Pass to template
    }

    return render(request, "reports/user_detail.html", context)
