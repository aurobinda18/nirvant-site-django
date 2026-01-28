from django.contrib import admin
from .models import Mentor, StudentProfile

# Register Mentor model
admin.site.register(Mentor)
admin.site.register(StudentProfile)

from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'mentor', 'priority', 'recipient_type', 'created_at', 'is_active')
    list_filter = ('priority', 'recipient_type', 'is_active', 'created_at')
    search_fields = ('title', 'message', 'mentor__name')
    list_editable = ('is_active',)