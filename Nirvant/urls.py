"""
URL configuration for Nirvant project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Import ALL views from Home app
from Home.views import home_view, courses_view, contact_view,terms_view, register,login_view, dashboard, logout_view
from team.views import team_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("courses/", courses_view, name="courses"),
    path("team/", team_view, name="team"),
    path("contact/", contact_view, name="contact"),
    path('terms/', terms_view, name='terms'),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),


]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)