from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, timedelta
from .models import EmailOTP
from .serializers import EmailOTPSerializer
from django.core.mail import send_mail
import random

def generate_otp(length=6):
    """
    Rastgele OTP oluştur.
    """
    return ''.join(random.choices('0123456789', k=length))

@api_view(['POST'])
def send_otp(request):
    """
    OTP gönder.
    """
    email = request.data.get('email')
    if not email:
        return Response({"error": "E-posta adresi gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

    # OTP oluştur
    otp = generate_otp()
    expires_at = now() + timedelta(hours=24)  # OTP 24 saat geçerli

    # Mevcut OTP'yi sil ve yenisini oluştur
    EmailOTP.objects.filter(email=email).delete()
    email_otp = EmailOTP.objects.create(email=email, otp=otp, expires_at=expires_at)

    # E-posta gönder
    send_mail(
        subject="E-posta Doğrulama Kodu",
        message=f"E-posta doğrulama kodunuz: {otp}",
        from_email="noreply@example.com",
        recipient_list=[email],
    )

    return Response({
        "message": "OTP gönderildi.",
        "email": email,
        "expires_at": email_otp.expires_at
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_otp(request):
    """
    OTP doğrula.
    """
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({"error": "E-posta ve OTP gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        email_otp = EmailOTP.objects.get(email=email, otp=otp)
        if email_otp.is_valid():
            # OTP geçerli, doğrulama başarılı
            email_otp.delete()  # Kullanıldıktan sonra OTP'yi sil
            return Response({"message": "OTP doğrulandı."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "OTP'nin süresi dolmuş."}, status=status.HTTP_400_BAD_REQUEST)
    except EmailOTP.DoesNotExist:
        return Response({"error": "Geçersiz OTP."}, status=status.HTTP_400_BAD_REQUEST)
