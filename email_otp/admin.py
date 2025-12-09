from django.contrib import admin
from .models import EmailOTP, ResponsiblePersonInvitation

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = [
        'email', 
        'code',  # ✅ 'otp' yerine 'code'
        'purpose', 
        'is_verified', 
        'created_at', 
        'expires_at',
        'is_expired_status'
    ]
    list_filter = ['purpose', 'is_verified', 'created_at']
    search_fields = ['email', 'code']
    readonly_fields = ['created_at', 'verified_at']
    ordering = ['-created_at']
    
    def is_expired_status(self, obj):
        """Süre dolmuş mu?"""
        return obj.is_expired()
    is_expired_status.short_description = 'Süresi Doldu'
    is_expired_status.boolean = True


@admin.register(ResponsiblePersonInvitation)
class ResponsiblePersonInvitationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'support_required_user',
        'responsible_email',
        'status',
        'created_at',
        'accepted_at',
        'is_expired_status'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['support_required_user__email', 'responsible_email']
    readonly_fields = ['created_at', 'accepted_at', 'otp']
    ordering = ['-created_at']
    
    def is_expired_status(self, obj):
        """Davet süresi dolmuş mu?"""
        return obj.otp.is_expired()
    is_expired_status.short_description = 'Süresi Doldu'
    is_expired_status.boolean = True
