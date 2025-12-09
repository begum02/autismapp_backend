from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

class EmailOTP(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registration'),
            ('verification', 'Verification'),
            ('password_reset', 'Password Reset'),
            ('responsible_invite', 'Responsible Person Invite'),
        ],
        default='verification'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='sent_otp_invitations'
    )
    
    class Meta:
        db_table = 'email_otp'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_verified']),
            models.Index(fields=['code', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.code} - {self.purpose}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        
        if not self.expires_at:
            # Purpose'a göre farklı süreler
            if self.purpose == 'responsible_invite':
                # Davet için 7 GÜN
                self.expires_at = timezone.now() + timedelta(days=7)
            elif self.purpose == 'password_reset':
                # Şifre sıfırlama için 1 SAAT
                self.expires_at = timezone.now() + timedelta(hours=1)
            else:
                # Genel doğrulama için 30 DAKİKA
                self.expires_at = timezone.now() + timedelta(minutes=30)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def create_otp(cls, email, purpose='verification', invited_by=None):
        """Yeni OTP oluştur - eski pending kodları sil"""
        # Eski kodları geçersiz yap
        cls.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).delete()
        
        # Yeni kod oluştur
        otp = cls.objects.create(
            email=email,
            purpose=purpose,
            invited_by=invited_by
        )
        return otp
    
    @classmethod
    def verify_code(cls, email, code):
        """Kodu doğrula"""
        try:
            otp = cls.objects.get(
                email=email,
                code=code,
                is_verified=False
            )
            
            if otp.is_expired():
                return False, "Kod süresi dolmuş", None
            
            otp.is_verified = True
            otp.verified_at = timezone.now()
            otp.save()
            
            return True, "Email başarıyla doğrulandı", otp
        
        except cls.DoesNotExist:
            return False, "Geçersiz kod", None
    
    def get_expiry_info(self):
        """Kalan süre bilgisi"""
        if self.is_expired():
            return "Süresi dolmuş"
        
        remaining = self.expires_at - timezone.now()
        
        if remaining.days > 0:
            return f"{remaining.days} gün"
        elif remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} saat"
        else:
            minutes = remaining.seconds // 60
            return f"{minutes} dakika"


class ResponsiblePersonInvitation(models.Model):
    """Sorumlu kişi davetleri"""
    support_required_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    responsible_email = models.EmailField()
    responsible_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_invitations'
    )
    otp = models.OneToOneField(
        EmailOTP,
        on_delete=models.CASCADE,
        related_name='invitation'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'responsible_person_invitations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.support_required_user.username} -> {self.responsible_email} ({self.status})"
    
    def get_status_display_turkish(self):
        """Türkçe durum"""
        status_map = {
            'pending': 'Bekliyor',
            'accepted': 'Kabul Edildi',
            'rejected': 'Reddedildi',
        }
        return status_map.get(self.status, self.status)
