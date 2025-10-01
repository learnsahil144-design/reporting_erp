from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views   # ✅ add this
from django.shortcuts import redirect
from reports.views import submit_report
from reports.views import admin_reports_overview


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('login/', auth_views.LoginView.as_view(), name='login'),   # ✅ use auth_views
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('report/', submit_report, name='submit_report'),
    path("admin-reports/", admin_reports_overview, name="admin_reports_overview"),
]
