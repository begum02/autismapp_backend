from django.contrib import admin
from .models import EmailOTP

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'created_at', 'expires_at', 'is_valid']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['email', 'otp']
    readonly_fields = ['created_at']
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Geçerli mi?'
