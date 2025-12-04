from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    """
    Genel görev istatistikleri
    """
    user = request.user
    
    total_tasks = Task.objects.filter(assigned_to=user).count()
    pending_tasks = Task.objects.filter(assigned_to=user, status='pending').count()
    in_progress_tasks = Task.objects.filter(assigned_to=user, status='in_progress').count()
    completed_tasks = Task.objects.filter(assigned_to=user, status='completed').count()
    cancelled_tasks = Task.objects.filter(assigned_to=user, status='cancelled').count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return Response({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'cancelled_tasks': cancelled_tasks,
        'completion_rate': round(completion_rate, 2)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_statistics(request, user_id):
    """
    Belirli bir kullanıcının görev istatistiklerini döndürür
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Yetki kontrolü
        if request.user.id != user_id and request.user.role != 'responsible_person' and not request.user.is_staff:
            return Response(
                {'error': 'Bu kullanıcının istatistiklerini görme yetkiniz yok'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Kullanıcının tüm görevleri
        total_tasks = Task.objects.filter(assigned_to=user).count()
        
        # Tamamlanan görevler
        completed_tasks = Task.objects.filter(
            assigned_to=user,
            status='completed'
        ).count()
        
        # Tamamlanma oranı
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return Response({
            'user_id': user_id,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': Task.objects.filter(assigned_to=user, status='pending').count(),
            'in_progress_tasks': Task.objects.filter(assigned_to=user, status='in_progress').count(),
            'cancelled_tasks': Task.objects.filter(assigned_to=user, status='cancelled').count(),
            'completion_rate': round(completion_rate, 2),
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Kullanıcı bulunamadı'},
            status=status.HTTP_404_NOT_FOUND
        )