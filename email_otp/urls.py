from django.urls import path
from . import views

app_name = 'email_otp'

urlpatterns = [
    # OTP işlemleri (AllowAny - kimlik doğrulama gerektirmez)
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    # Sorumlu kişi davet sistemi (IsAuthenticated - giriş gerektirir)
    path('invite/', views.invite_responsible_person, name='invite_responsible'),
    path('accept-invitation/', views.accept_invitation, name='accept_invitation'),
    path('invitations/', views.list_invitations, name='list_invitations'),
    path('invitations/<int:invitation_id>/resend/', views.resend_invitation, name='resend_invitation'),
    path('invitations/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    path('invitations/<int:invitation_id>/reject/', views.reject_invitation, name='reject_invitation'),
]

