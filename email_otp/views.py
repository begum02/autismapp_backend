from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP, ResponsiblePersonInvitation
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    InviteResponsiblePersonSerializer,
    ResponsiblePersonInvitationSerializer,
    AcceptInvitationSerializer,
)
import traceback


# ==================== OTP SİSTEMİ ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """OTP kodu gönder"""
    try:
        print("="*80)
        print("📧 OTP GÖNDERME İSTEĞİ")
        print("="*80)
        print(f"📦 Request data: {request.data}")
        print("="*80)
        
        serializer = SendOTPSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        purpose = serializer.validated_data.get('purpose', 'verification')
        
        print(f"✅ Email: {email}, Purpose: {purpose}")
        
        # Mevcut OTP'leri sil
        EmailOTP.objects.filter(email=email, purpose=purpose, is_verified=False).delete()
        
        # Yeni OTP oluştur
        otp = EmailOTP.create_otp(email=email, purpose=purpose)
        
        print(f"🔑 OTP oluşturuldu - Code: {otp.code}")
        
        # Email gönder
        try:
            from .utils import format_otp_email
            subject, message = format_otp_email(otp.code, purpose)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            print(f"✅ Email gönderildi: {email}")
            
        except Exception as email_error:
            print(f"❌ Email gönderme hatası: {str(email_error)}")
            traceback.print_exc()
        
        print("="*80)
        
        return Response({
            'message': 'OTP kodu gönderildi',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ OTP gönderme hatası: {str(e)}")
        traceback.print_exc()
        return Response(
            {'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """OTP kodunu doğrula"""
    try:
        print("="*80)
        print("🔐 OTP DOĞRULAMA İSTEĞİ")
        print("="*80)
        print(f"📦 Request data: {request.data}")
        print("="*80)
        
        serializer = VerifyOTPSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        # OTP'yi bul
        try:
            otp = EmailOTP.objects.get(
                email=email,
                code=code,
                is_verified=False
            )
        except EmailOTP.DoesNotExist:
            print(f"❌ OTP bulunamadı: {email} - {code}")
            return Response({
                'detail': 'Geçersiz OTP kodu'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Süre kontrolü
        if otp.is_expired():
            print(f"❌ OTP süresi dolmuş: {email}")
            return Response({
                'detail': 'OTP kodunun süresi dolmuş'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP'yi doğrula
        otp.is_verified = True
        otp.verified_at = timezone.now()
        otp.save()
        
        print(f"✅ OTP doğrulandı: {email}")
        print("="*80)
        
        return Response({
            'message': 'OTP başarıyla doğrulandı',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ OTP doğrulama hatası: {str(e)}")
        traceback.print_exc()
        return Response(
            {'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== DAVET SİSTEMİ ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_responsible_person(request):
    """Sorumlu kişi davet et"""
    try:
        print("="*80)
        print("📧 SORUMLU KİŞİ DAVET İSTEĞİ")
        print("="*80)
        print(f"👤 User: {request.user.email} (ID: {request.user.id})")
        print(f"📦 Request data: {request.data}")
        print("="*80)
        
        serializer = InviteResponsiblePersonSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        responsible_email = serializer.validated_data['responsible_email']
        print(f"✅ Validated email: {responsible_email}")
        
        # Mevcut pending davet kontrolü
        existing_invitation = ResponsiblePersonInvitation.objects.filter(
            support_required_user=request.user,
            responsible_email=responsible_email,
            status='pending'
        ).first()
        
        if existing_invitation:
            if not existing_invitation.otp.is_expired():
                print(f"⚠️  Aktif davet var (ID: {existing_invitation.id})")
                return Response({
                    'detail': 'Bu email için zaten aktif bir davet var'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(f"🗑️  Eski davet siliniyor (ID: {existing_invitation.id})")
                existing_invitation.otp.delete()
        
        # OTP oluştur
        otp = EmailOTP.create_otp(
            email=responsible_email,
            purpose='responsible_invite',
            invited_by=request.user
        )
        print(f"🔑 OTP oluşturuldu - Code: {otp.code}, Expires: {otp.expires_at}")
        
        # Davet oluştur
        invitation = ResponsiblePersonInvitation.objects.create(
            support_required_user=request.user,
            responsible_email=responsible_email,
            otp=otp,
            status='pending'
        )
        print(f"✅ Davet oluşturuldu - ID: {invitation.id}")
        
        # Email gönder
        try:
            subject = 'PlanBuddy Uygulamasına Davet'
            message = f"""
Merhaba,

PlanBuddy uygulamasında sorumlu kişi olarak davet edildiniz.

Davet Kodu: {otp.code}

Bu kodu kullanarak daveti kabul edebilirsiniz.
Kod {otp.get_expiry_info()} geçerlidir.

PlanBuddy Ekibi
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[responsible_email],
                fail_silently=False,
            )
            
            print(f"✅ Email gönderildi: {responsible_email}")
            
        except Exception as email_error:
            print(f"❌ Email gönderme hatası: {str(email_error)}")
            traceback.print_exc()
        
        response_data = {
            'message': 'Davet başarıyla gönderildi',
            'invitation': ResponsiblePersonInvitationSerializer(invitation).data
        }
        
        print(f"✅ Response hazır")
        print("="*80)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ BEKLENMEYEN HATA: {str(e)}")
        traceback.print_exc()
        print("="*80)
        return Response(
            {'detail': f'Sunucu hatası: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_invitations(request):
    """Kullanıcının gönderdiği davetleri listele"""
    try:
        print("="*80)
        print("📋 DAVET LİSTESİ İSTEĞİ")
        print(f"👤 User: {request.user.email}")
        print("="*80)
        
        invitations = ResponsiblePersonInvitation.objects.filter(
            support_required_user=request.user
        ).select_related('otp').order_by('-created_at')
        
        serializer = ResponsiblePersonInvitationSerializer(invitations, many=True)
        
        stats = {
            'total': invitations.count(),
            'pending': invitations.filter(status='pending').count(),
            'accepted': invitations.filter(status='accepted').count(),
            'rejected': invitations.filter(status='rejected').count(),
        }
        
        print(f"✅ {invitations.count()} davet bulundu")
        print(f"📊 Stats: {stats}")
        print("="*80)
        
        return Response({
            'invitations': serializer.data,
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Davet listesi hatası: {str(e)}")
        traceback.print_exc()
        return Response(
            {'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invitation(request):
    """Daveti kabul et"""
    try:
        print("="*80)
        print("✅ DAVET KABUL İSTEĞİ")
        print(f"📦 Request data: {request.data}")
        print("="*80)
        
        serializer = AcceptInvitationSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        invitation_id = serializer.validated_data['invitation_id']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            invitation = ResponsiblePersonInvitation.objects.select_related('otp').get(
                id=invitation_id,
                status='pending'
            )
        except ResponsiblePersonInvitation.DoesNotExist:
            print(f"❌ Davet bulunamadı: {invitation_id}")
            return Response({
                'detail': 'Geçersiz davet'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if invitation.otp.code != otp_code:
            print(f"❌ OTP yanlış: {otp_code}")
            return Response({
                'detail': 'Geçersiz davet kodu'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if invitation.otp.is_expired():
            print(f"❌ OTP süresi dolmuş")
            return Response({
                'detail': 'Davet kodu süresi dolmuş'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.otp.is_verified = True
        invitation.otp.verified_at = timezone.now()
        invitation.otp.save()
        invitation.save()
        
        print(f"✅ Davet kabul edildi - ID: {invitation.id}")
        print("="*80)
        
        return Response({
            'message': 'Davet başarıyla kabul edildi',
            'invitation': ResponsiblePersonInvitationSerializer(invitation).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Davet kabul hatası: {str(e)}")
        traceback.print_exc()
        return Response(
            {'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_invitation(request, invitation_id):
    """Daveti yeniden gönder"""
    try:
        invitation = ResponsiblePersonInvitation.objects.select_related('otp').get(
            id=invitation_id,
            support_required_user=request.user
        )
        
        old_otp = invitation.otp
        new_otp = EmailOTP.create_otp(
            email=invitation.responsible_email,
            purpose='responsible_invite',
            invited_by=request.user
        )
        
        invitation.otp = new_otp
        invitation.status = 'pending'
        invitation.save()
        
        old_otp.delete()
        
        # Email gönder
        subject = 'PlanBuddy Uygulamasına Davet'
        message = f"""
Merhaba,

PlanBuddy uygulamasında sorumlu kişi olarak davet edildiniz.

Davet Kodu: {new_otp.code}

Bu kodu kullanarak daveti kabul edebilirsiniz.
Kod {new_otp.get_expiry_info()} geçerlidir.

PlanBuddy Ekibi
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[invitation.responsible_email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Davet yeniden gönderildi',
            'invitation': ResponsiblePersonInvitationSerializer(invitation).data
        }, status=status.HTTP_200_OK)
        
    except ResponsiblePersonInvitation.DoesNotExist:
        return Response({
            'detail': 'Davet bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_invitation(request, invitation_id):
    """Daveti iptal et"""
    try:
        invitation = ResponsiblePersonInvitation.objects.get(
            id=invitation_id,
            support_required_user=request.user
        )
        
        invitation.status = 'cancelled'
        invitation.save()
        
        return Response({
            'message': 'Davet iptal edildi'
        }, status=status.HTTP_200_OK)
        
    except ResponsiblePersonInvitation.DoesNotExist:
        return Response({
            'detail': 'Davet bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def reject_invitation(request, invitation_id):
    """Daveti reddet"""
    try:
        invitation = ResponsiblePersonInvitation.objects.get(id=invitation_id)
        
        invitation.status = 'rejected'
        invitation.save()
        
        return Response({
            'message': 'Davet reddedildi'
        }, status=status.HTTP_200_OK)
        
    except ResponsiblePersonInvitation.DoesNotExist:
        return Response({
            'detail': 'Davet bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
