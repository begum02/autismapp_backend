import random
import string
from datetime import timedelta
from django.utils import timezone


def generate_otp(length=6):
    """OTP kodu oluştur"""
    return ''.join(random.choices(string.digits, k=length))


def is_otp_expired(created_at, expiry_minutes=10):
    """
    OTP kodunun süresinin dolup dolmadığını kontrol et
    
    Args:
        created_at: OTP oluşturulma zamanı
        expiry_minutes: Geçerlilik süresi (dakika)
    
    Returns:
        bool: Süresi dolmuşsa True, dolmamışsa False
    """
    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    return timezone.now() > expiry_time


def format_invitation_email(invitation_code, support_user_name=None):
    """
    Davet email içeriğini formatla
    
    Args:
        invitation_code: Davet kodu
        support_user_name: Daveti gönderen kişinin adı (opsiyonel)
    
    Returns:
        tuple: (subject, message)
    """
    if support_user_name:
        subject = f'{support_user_name} Sizi PlanBuddy Uygulamasına Davet Etti'
        greeting = f'{support_user_name} sizi PlanBuddy uygulamasında sorumlu kişi olarak ekledi.'
    else:
        subject = 'PlanBuddy Uygulamasına Davet'
        greeting = 'PlanBuddy uygulamasında sorumlu kişi olarak davet edildiniz.'
    
    message = f"""
Merhaba,

{greeting}

Davet Kodu: {invitation_code}

Bu kodu kullanarak daveti kabul edebilirsiniz.
Kod 24 saat geçerlidir.

PlanBuddy Ekibi
    """
    
    return subject, message


def format_otp_email(otp_code, purpose='verification'):
    """OTP email içeriğini formatla"""
    purpose_messages = {
        'registration': {
            'subject': 'PlanBuddy Kayıt Doğrulama Kodu',
            'message': f"""
Merhaba,

PlanBuddy uygulamasına kayıt olduğunuz için teşekkür ederiz.

Doğrulama Kodunuz: {otp_code}

Bu kod 10 dakika geçerlidir.

PlanBuddy Ekibi
            """
        },
        'verification': {
            'subject': 'PlanBuddy Doğrulama Kodu',
            'message': f"""
Merhaba,

Email adresinizi doğrulamak için aşağıdaki kodu kullanın.

Doğrulama Kodunuz: {otp_code}

Bu kod 10 dakika geçerlidir.

PlanBuddy Ekibi
            """
        },
        'password_reset': {
            'subject': 'PlanBuddy Şifre Sıfırlama Kodu',
            'message': f"""
Merhaba,

Şifrenizi sıfırlamak için aşağıdaki kodu kullanın.

Sıfırlama Kodunuz: {otp_code}

Bu kodu talep etmediyseniz, bu emaili göz ardı edebilirsiniz.
Bu kod 10 dakika geçerlidir.

PlanBuddy Ekibi
            """
        }
    }
    
    template = purpose_messages.get(purpose, purpose_messages['verification'])
    return template['subject'], template['message']


def validate_email(email):
    """
    Email formatını kontrol et
    
    Args:
        email: Email adresi
    
    Returns:
        bool: Geçerli ise True, değilse False
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None