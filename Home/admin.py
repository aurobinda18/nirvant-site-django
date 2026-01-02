from django.contrib import admin

# Register your models here.
from Home.models import SuperMentor,EmailOTP
@admin.register(SuperMentor)
class SuperMentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'expertise')

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'first_name', 'created_at')