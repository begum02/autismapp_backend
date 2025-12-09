from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email adresi zorunludur')
        
        email = self.normalize_email(email)
        
        # Username otomatik oluştur (eğer verilmemişse)
        if not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0] + str(uuid.uuid4())[:8]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'individual')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model
    - 3 farklı kullanıcı tipi:
        * individual: Kendi kendini yöneten birey (bağımsız kullanıcı)
        * support_required_individual: Desteğe gereksinimi olan birey (otizm spektrumlu)
        * responsible_person: Sorumlu kişi (ebeveyn / öğretmen / bakıcı / terapist)
    """

    ROLE_CHOICES = [
        ('individual', 'Birey'),
        ('support_required_individual', 'Destek Gereksinimli Birey'),
        ('responsible_person', 'Sorumlu Kişi'),
    ]
    
    username = models.CharField(
        max_length=150, 
        unique=True,
        verbose_name='Kullanıcı Adı'
    )
    email = models.EmailField(unique=True, verbose_name='E-posta')
    full_name = models.CharField(max_length=255, blank=True, verbose_name='Ad Soyad')
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='individual',
        verbose_name='Rol'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        verbose_name='Profil Resmi'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # createsuperuser için
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
    
    def __str__(self):
        return f"{self.full_name or self.email} ({self.get_role_display()})"
    
    def is_individual(self):
        """Bağımsız birey mi?"""
        return self.role == 'individual'
    
    def is_support_required(self):
        """Destek gereksinimli birey mi?"""
        return self.role == 'support_required_individual'
    
    def is_responsible(self):
        """Sorumlu kişi mi?"""
        return self.role == 'responsible_person'


class SupportRelationship(models.Model):
    """
    Sorumlu kişi ile destek gereksinimli birey arasındaki ilişki
    (Sadece responsible_person ve support_required_individual arasında olabilir)
    """
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='supported_individuals',
        limit_choices_to={'role': 'responsible_person'},
        verbose_name='Sorumlu Kişi'
    )
    individual = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='responsible_persons',
        limit_choices_to={'role': 'support_required_individual'},
        verbose_name='Destek Gereksinimli Birey'
    )
    relationship_type = models.CharField(
        max_length=50,
        choices=[
            ('parent', 'Ebeveyn'),
            ('guardian', 'Vasi'),
            ('caregiver', 'Bakıcı'),
            ('therapist', 'Terapist'),
            ('teacher', 'Öğretmen'),
            ('other', 'Diğer'),
        ],
        default='parent',
        verbose_name='İlişki Türü'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    class Meta:
        db_table = 'users_support_relationship'
        verbose_name = 'Destek İlişkisi'
        verbose_name_plural = 'Destek İlişkileri'
        unique_together = [('responsible_person', 'individual')]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.responsible_person.full_name} -> {self.individual.full_name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Aynı kişi hem sorumlu hem birey olamaz
        if self.responsible_person == self.individual:
            raise ValidationError('Sorumlu kişi ve birey aynı olamaz')
        
        # Sorumlu kişi role kontrolü
        if self.responsible_person.role != 'responsible_person':
            raise ValidationError('Sorumlu kişi rolü "responsible_person" olmalıdır')
        
        # Birey role kontrolü
        if self.individual.role != 'support_required_individual':
            raise ValidationError('Birey rolü "support_required_individual" olmalıdır')
