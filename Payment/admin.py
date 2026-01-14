from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'course_name', 
        'plan_type', 
        'duration_text', 
        'course_price', 
        'original_price', 
        'discount_percentage',
        'is_active',
        'display_order',
        'created_at'
    ]
    
    list_editable = ['is_active', 'display_order', 'discount_percentage']
    
    list_filter = ['plan_type', 'is_active']
    
    search_fields = ['course_name', 'course_description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_name', 'course_description', 'plan_type', 'is_active', 'display_order')
        }),
        ('Duration', {
            'fields': ('duration_days', 'duration_text')
        }),
        ('Pricing', {
            'fields': ('course_price', 'original_price', 'discount_percentage')
        }),
        ('Button', {
            'fields': ('button_text',)
        }),
    )