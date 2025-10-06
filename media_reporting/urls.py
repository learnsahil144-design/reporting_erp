from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from reports.views import submit_report, admin_reports_overview, export_reports_excel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    
    # 🔐 Auth
    path(
        'login/',
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # 📝 Reports
    path('report/', submit_report, name='submit_report'),
    path("admin-reports/", admin_reports_overview, name="admin_reports_overview"),

    # 📤 Excel Export
    path("export/excel/", export_reports_excel, name="export_reports_excel"),
]
