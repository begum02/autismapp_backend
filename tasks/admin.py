from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'assigned_to', 'created_by', 'status', 'scheduled_date', 'priority']
    list_filter = ['status', 'priority', 'task_type', 'category', 'scheduled_date', 'created_at']
    search_fields = ['title', 'description', 'assigned_to__email', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Görev Bilgileri', {
            'fields': ('assigned_to', 'created_by', 'title', 'description', 'task_type', 'category')
        }),
        ('Zaman Ayarları', {
            'fields': ('scheduled_date', 'start_time', 'end_time', 'estimated_duration')
        }),
        ('Medya', {
            'fields': ('lottie_animation', 'lottie_url', 'video_file', 'video_url', 'image', 'audio_file')
        }),
        ('Durum', {
            'fields': ('status', 'priority', 'difficulty_level', 'notes')
        }),
        ('Tamamlanma', {
            'fields': ('completed', 'completed_at', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize edilmiş queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('assigned_to', 'created_by')