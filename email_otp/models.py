from django.db import models
from django.utils.timezone import now, timedelta

class EmailOTP(models.Model):
    email = models.EmailField(unique=True, verbose_name="E-posta Adresi")
    otp = models.CharField(max_length=6, verbose_name="OTP Kodu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")
    expires_at = models.DateTimeField(verbose_name="Geçerlilik Süresi")

    def is_valid(self):
        """
        OTP'nin geçerli olup olmadığını kontrol eder.
        """
        return now() < self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp}"

    class Meta:
        verbose_name = "E-posta OTP"
        verbose_name_plural = "E-posta OTP'leri"
        ordering = ['-created_at']
