from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from reports.views import (
    submit_report,
    admin_reports_overview,
    user_report_detail,
    export_reports_excel,
    user_report_preview,
    user_dashboard,
    admin_change_password,
)

urlpatterns = [

    # 🔧 Django Admin (Obscured for security)
    path("management-portal/", admin.site.urls),

    # 🏠 Default → Dashboard
    path("", user_dashboard, name="home"),

    # 🔐 Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout"
    ),

    # 🏠 User Dashboard
    path("dashboard/", user_dashboard, name="user_dashboard"),

    # 📝 Submit Report (User Side)
    path("report/", submit_report, name="submit_report"),

    # 📊 Admin Report Overview (Date Filter + Export)
    path("admin-reports/", admin_reports_overview, name="admin_reports_overview"),

    # 👤 Admin: View all reports of one specific user
    path(
        "admin-reports/user/<str:username>/",
        user_report_detail,
        name="user_report_detail"
    ),

    # 📤 Export to Excel
    path(
        "export/excel/",
        export_reports_excel,
        name="export_reports_excel"
    ),

    # 👤 User: Preview their own report for any date
    path(
        "my-report/<str:date>/",
        user_report_preview,
        name="user_report_preview"
    ),

    # 🔐 Admin: Reset password for any user
    path(
        "admin-reports/user/password-reset/<int:user_id>/",
        admin_change_password,
        name="staff_password_reset"
    ),
]
