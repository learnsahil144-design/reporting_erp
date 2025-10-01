from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .forms import ReportForm
from .models import Report


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


@staff_member_required
def admin_reports_overview(request):
    team_filter = request.GET.get("team")
    date_filter = request.GET.get("date")

    reports = Report.objects.all().select_related("user")
    if team_filter:
        reports = reports.filter(user__team=team_filter)  # ✅ FIXED
    if date_filter:
        reports = reports.filter(custom_date=date_filter)

    reports_by_team = (
        reports.values("user__team")  # ✅ FIXED
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    reports_by_user = (
        reports.values("user__username")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return render(
        request,
        "reports/admin_overview.html",
        {
            "reports": reports,
            "reports_by_team": reports_by_team,
            "reports_by_user": reports_by_user,
        },
    )
