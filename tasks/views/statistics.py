from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Task

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
def user_statistics_view(request, user_id):
    """
    Kullanıcının görev istatistikleri
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Kullanıcı bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
    
    total_tasks = Task.objects.filter(assigned_to=user).count()
    completed_tasks = Task.objects.filter(assigned_to=user, status='completed').count()
    pending_tasks = Task.objects.filter(assigned_to=user, status='pending').count()
    in_progress_tasks = Task.objects.filter(assigned_to=user, status='in_progress').count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return Response({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': round(completion_rate, 2),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_completed_count_view(request):
    """
    Bugün tamamlanan görev sayısı
    """
    today = timezone.now().date()
    
    count = Task.objects.filter(
        status='completed',
        updated_at__date=today
    ).count()
    
    return Response({
        'count': count,
        'date': today
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignable_users_view(request):
    """
    Sorumlu kişinin atayabileceği kullanıcılar
    """
    current_user = request.user
    
    if current_user.role == 'responsible_person':
        users = User.objects.filter(
            role='support_required_individual'
        ).values('id', 'email', 'username', 'full_name', 'profile_picture', 'role')
        
        return Response({
            'count': len(users),
            'results': list(users)
        }, status=status.HTTP_200_OK)
    
    return Response({
        'count': 0,
        'results': []
    }, status=status.HTTP_200_OK)