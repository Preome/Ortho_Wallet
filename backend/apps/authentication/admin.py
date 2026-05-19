from django.contrib import admin
from .models import User, OTP, UserSession

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'phone_number', 'is_verified', 'has_pin']
    search_fields = ['email', 'full_name', 'phone_number']
    list_filter = ['is_verified', 'has_pin']

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'purpose', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used', 'is_used']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active']