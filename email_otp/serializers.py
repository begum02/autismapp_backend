from rest_framework import serializers
from .models import EmailOTP, ResponsiblePersonInvitation
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOTPSerializer(serializers.ModelSerializer):
    is_expired_status = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailOTP
        fields = [
            'id',
            'email',
            'code',
            'purpose',
            'is_verified',
            'verified_at',
            'created_at',
            'expires_at',
            'is_expired_status'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'verified_at']
    
    def get_is_expired_status(self, obj):
        return obj.is_expired()


class SendOTPSerializer(serializers.Serializer):
    """OTP gönderme için serializer"""
    email = serializers.EmailField(required=True)
    purpose = serializers.ChoiceField(
        choices=['registration', 'password_reset', 'responsible_person_invitation'],
        default='registration'
    )
    
    def validate_email(self, value):
        """Email formatı kontrolü"""
        return value.lower().strip()


class VerifyOTPSerializer(serializers.Serializer):
    """OTP doğrulama için serializer"""
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_email(self, value):
        return value.lower().strip()
    
    def validate_code(self, value):
        return value.strip()


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']
        read_only_fields = ['id', 'email', 'role']


class ResponsiblePersonInvitationSerializer(serializers.ModelSerializer):
    support_required_user_detail = UserMinimalSerializer(source='support_required_user', read_only=True)
    is_expired_status = serializers.SerializerMethodField()
    invitation_code = serializers.CharField(source='otp.code', read_only=True)  # ✅ OTP'den al
    created_at = serializers.DateTimeField(source='otp.created_at', read_only=True)  # ✅ OTP'den al
    
    class Meta:
        model = ResponsiblePersonInvitation
        fields = [
            'id',
            'support_required_user',
            'support_required_user_detail',
            'responsible_email',
            'invitation_code',  # ✅ Frontend için
            'status',
            'created_at',
            'accepted_at',
            'is_expired_status',
        ]
        read_only_fields = ['id', 'created_at', 'accepted_at', 'invitation_code']
    
    def get_is_expired_status(self, obj):
        """OTP süresi dolmuş mu?"""
        return obj.otp.is_expired() if obj.otp else True


class InviteResponsiblePersonSerializer(serializers.Serializer):
    """Sorumlu kişi davet etme için serializer"""
    responsible_email = serializers.EmailField(required=True)
    
    def validate_responsible_email(self, value):
        """Email formatı kontrolü"""
        return value.lower().strip()


# ✅ AcceptInvitationSerializer ekle
class AcceptInvitationSerializer(serializers.Serializer):
    """Davet kabul etme için serializer"""
    invitation_id = serializers.IntegerField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_otp_code(self, value):
        return value.strip()


# ✅ ResendInvitationSerializer ekle
class ResendInvitationSerializer(serializers.Serializer):
    """Davet yeniden gönderme için serializer"""
    invitation_id = serializers.IntegerField(required=True)