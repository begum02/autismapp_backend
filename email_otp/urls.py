from django.urls import path
from .views import send_otp, verify_otp

urlpatterns = [
    path('send/', send_otp, name='send_otp'),
    path('verify/', verify_otp, name='verify_otp'),
]