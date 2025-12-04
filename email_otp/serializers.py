from rest_framework import serializers
from .models import EmailOTP
from django.utils.timezone import now

class EmailOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOTP
        fields = ['email', 'otp', 'created_at', 'expires_at']

    def validate_email(self, value):
        """
        E-posta doğrulama.
        """
        if EmailOTP.objects.filter(email=value, expires_at__gte=now()).exists():
            raise serializers.ValidationError("Bu e-posta için zaten geçerli bir OTP mevcut.")
        return value