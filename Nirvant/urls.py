# urls.py - CORRECTED VERSION
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Import ALL views from Home app
from Home.views import home_view, courses_view, contact_view, terms_view, register, login_view, dashboard, logout_view, CustomPasswordResetView
from team.views import team_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("courses/", courses_view, name="courses"),
    path("team/", team_view, name="team"),
    path("contact/", contact_view, name="contact"),  # FIXED: removed extra )
    path('terms/', terms_view, name='terms'),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    
    # ==================== PASSWORD RESET URLS ====================
    # Enter email for password reset - USE CUSTOM VIEW
    path('password-reset/', 
        CustomPasswordResetView.as_view(),
        name='password_reset'),
    
    # Email sent confirmation
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), 
        name='password_reset_done'),
    
    # Reset password form (with token)
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/password-reset-complete/'
        ), 
        name='password_reset_confirm'),
    
    # Password reset complete
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ), 
        name='password_reset_complete'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)