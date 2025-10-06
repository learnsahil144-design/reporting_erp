from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
from .forms import ReportForm
from .models import Report, User
import pandas as pd


# ------------------------------
# 🧾 USER REPORT SUBMISSION
# ------------------------------
@login_required
def submit_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("submit_report")
    else:
        form = ReportForm(user=request.user)
    return render(request, "reports/submit_report.html", {"form": form})


# ------------------------------
# 🧠 ADMIN REPORT OVERVIEW
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

    # ✅ Aggregations
    reports_by_team = (
        reports.values("user__team")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    reports_by_user = (
        reports.values("user__username")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # ✅ To populate dropdowns
    teams = User.objects.values_list("team", flat=True).distinct()
    users = User.objects.all()

    return render(
        request,
        "reports/admin_overview.html",
        {
            "reports": reports,
            "reports_by_team": reports_by_team,
            "reports_by_user": reports_by_user,
            "teams": teams,
            "users": users,
            "selected_team": team_filter,
            "selected_user": user_filter,
        },
    )


# ------------------------------
# 📤 EXPORT TO EXCEL
# ------------------------------
@staff_member_required
def export_reports_excel(request):
    """Export all (or filtered) reports to Excel."""
    reports = Report.objects.select_related("user").all()

    # ✅ Apply same filters as overview
    team = request.GET.get("team")
    user = request.GET.get("user")
    date = request.GET.get("date")

    if team:
        reports = reports.filter(user__team=team)
    if user:
        reports = reports.filter(user__username=user)
    if date:
        reports = reports.filter(custom_date=date)

    # ✅ Prepare export data
    data = []
    for r in reports:
        data.append({
            "User": r.user.username,
            "Team": r.user.team,
            "Shift": r.get_shift_display(),
            "Report Date": r.custom_date or r.date,
            "Submitted At": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "Tasks": ", ".join([f"{k}: {v}" for k, v in r.tasks.items()]),
            "Notes": r.notes or "",
            "Status": "Late" if r.is_late_submission else "On Time",
        })

    if not data:
        data = [{"Info": "No reports found for selected filters"}]

    df = pd.DataFrame(data)

    # ✅ Generate Excel response
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="reports.xlsx"'
    df.to_excel(response, index=False)
    return response
