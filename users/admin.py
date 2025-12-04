from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SupportRelationship


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin Panel"""
    
    list_display = ['id', 'email', 'username', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'full_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('full_name', 'role', 'profile_picture')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(SupportRelationship)
class SupportRelationshipAdmin(admin.ModelAdmin):
    """Destek İlişkileri Admin Panel"""
    
    list_display = [
        'id', 
        'responsible_person', 
        'individual', 
        'relationship_type', 
        'is_active', 
        'created_at'
    ]
    list_filter = ['relationship_type', 'is_active', 'created_at']
    search_fields = [
        'responsible_person__email', 
        'responsible_person__full_name',
        'individual__email', 
        'individual__full_name'
    ]
    raw_id_fields = ['responsible_person', 'individual']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('İlişki Bilgileri', {
            'fields': ('responsible_person', 'individual', 'relationship_type')
        }),
        ('Durum', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize edilmiş queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('responsible_person', 'individual')
