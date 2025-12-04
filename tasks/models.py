from django.db import models
from django.conf import settings

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
    ]
    
    CATEGORY_CHOICES = [
        ('hygiene', 'Hijyen'),
        ('education', 'Eğitim'),
        ('social', 'Sosyal'),
        ('health', 'Sağlık'),
        ('other', 'Diğer'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('single', 'Tekli Görev'),
        ('routine', 'Rutin Görev'),
    ]
    
    # Kullanıcı ilişkileri
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name='Atanan Kullanıcı',
        db_column='user_id'  # Database'de user_id olarak kayıtlı
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Oluşturan'
    )
    
    # Görev Bilgileri
    title = models.CharField(max_length=200, verbose_name='Başlık')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default='single',
        verbose_name='Görev Tipi'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Kategori'
    )
    
    # Zaman Bilgileri
    scheduled_date = models.DateField(verbose_name='Tarih', db_column='date')
    start_time = models.TimeField(verbose_name='Başlangıç Saati')
    end_time = models.TimeField(blank=True, null=True, verbose_name='Bitiş Saati')
    estimated_duration = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Tahmini Süre (dakika)'
    )
    
    # Medya
    lottie_animation = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Lottie Animasyon'
    )
    lottie_url = models.URLField(blank=True, verbose_name='Lottie URL')
    video_file = models.FileField(
        upload_to='tasks/videos/',
        blank=True,
        null=True,
        verbose_name='Video Dosyası'
    )
    video_url = models.URLField(blank=True, verbose_name='Video URL')
    image = models.ImageField(
        upload_to='tasks/images/',
        blank=True,
        null=True,
        verbose_name='Görsel'
    )
    audio_file = models.FileField(
        upload_to='tasks/audio/',
        blank=True,
        null=True,
        verbose_name='Ses Dosyası'
    )
    
    # Durum
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Durum'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Öncelik'
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name='Zorluk Seviyesi'
    )
    notes = models.TextField(blank=True, verbose_name='Notlar')
    
    # Tamamlanma
    completed = models.BooleanField(default=False, verbose_name='Tamamlandı mı?')
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tamamlanma Zamanı'
    )
    
    # Zaman damgaları (EKLENEN ALANLAR)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Zamanı')
    
    class Meta:
        db_table = 'tasks_task'
        verbose_name = 'Görev'
        verbose_name_plural = 'Görevler'
        ordering = ['-scheduled_date', '-start_time']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.email}"
    
    @property
    def user(self):
        """Admin panelinde uyumluluk için"""
        return self.assigned_to
    
    @property
    def date(self):
        """Admin panelinde uyumluluk için"""
        return self.scheduled_date