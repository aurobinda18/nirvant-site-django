# urls.py - CORRECTED VERSION
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path
from dashboard.views import profile_view, mentor_view, mentor_dashboard, assign_students
from dashboard.views import progress_view
from dashboard.views import studypack_view,assign_batch,manage_test_series,upload_pyqs
from django.views.static import serve
from dashboard.views import view_pdf, download_pdf,send_notices

# Import ALL views from Home app
from Home.views import (
    home_view, 
    courses_view, 
    contact_view, 
    terms_view, 
    register, 
    login_view, 
    dashboard, 
    logout_view, 
    CustomPasswordResetView,
    checkout_view  # ONLY THIS LINE ADDED
)
from team.views import team_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("courses/", courses_view, name="courses"),
    path("checkout/", checkout_view, name="checkout"),  # This line stays as is
    path("team/", team_view, name="team"),
    path("contact/", contact_view, name="contact"),
    path('terms/', terms_view, name='terms'),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    
    # ==================== PASSWORD RESET URLS ====================
    path('password-reset/', 
        CustomPasswordResetView.as_view(),
        name='password_reset'),
    
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), 
        name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/password-reset-complete/'
        ), 
        name='password_reset_confirm'),
    
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ), 
        name='password_reset_complete'),

    path('dashboard/profile/', profile_view, name='profile'),
    path('dashboard/mentor/', mentor_view, name='mentor'),
    path('dashboard/mentor-dashboard/', mentor_dashboard, name='mentor_dashboard'),
    path('dashboard/assign-students/', assign_students, name='assign_students'),
    path('mentor-dashboard/', mentor_dashboard, name='mentor_dashboard'),
    path('dashboard/progress/', progress_view, name='progress'),
    path('dashboard/studypack/', studypack_view, name='studypack'),
    path('dashboard/assign-batch/', assign_batch, name='assign_batch'),
    path('dashboard/manage-test-series/', manage_test_series, name='manage_test_series'),
    path('dashboard/upload-pyqs/', upload_pyqs, name='upload_pyqs'),
    path('view-pdf/<int:pdf_id>/', view_pdf, name='view_pdf'),
    path('download-pdf/<int:pdf_id>/', download_pdf, name='download_pdf'),
    path('dashboard/send-notices/', send_notices, name='send_notices'),

]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)