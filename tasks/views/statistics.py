from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Task
from datetime import datetime, time

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_time_statistics(request):
    """
    Görev zaman istatistikleri
    """
    user = request.user
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    today_completed = Task.objects.filter(assigned_to=user, status='completed', updated_at__date=today).count()
    today_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__date=today).count()
    today_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__date=today).count()
    
    start_datetime = datetime.combine(start_of_week, time.min, tzinfo=timezone.get_current_timezone())
    end_datetime = datetime.combine(today, time.max, tzinfo=timezone.get_current_timezone())

    week_completed = Task.objects.filter(
        assigned_to=user,
        status='completed',
        updated_at__range=[start_datetime, end_datetime]
    ).count()
    week_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__range=[start_of_week, today]).count()
    week_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__range=[start_of_week, today]).count()
    
    month_completed = Task.objects.filter(assigned_to=user, status='completed', updated_at__month=today.month).count()
    month_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__month=today.month).count()
    month_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__month=today.month).count()
    
    return Response({
        "today_completed": today_completed,
        "today_cancelled": today_cancelled,
        "today_in_progress": today_in_progress,
        "week_completed": week_completed,
        "week_cancelled": week_cancelled,
        "week_in_progress": week_in_progress,
        "month_completed": month_completed,
        "month_cancelled": month_cancelled,
        "month_in_progress": month_in_progress
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_time_statistics_view(request, user_id):
    """
    Kullanıcıya özel görev zaman istatistikleri
    """
    user = User.objects.get(id=user_id)
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    today_completed = Task.objects.filter(assigned_to=user, status='completed', updated_at__date=today).count()
    today_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__date=today).count()
    today_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__date=today).count()

    start_datetime = datetime.combine(start_of_week, time.min, tzinfo=timezone.get_current_timezone())
    end_datetime = datetime.combine(today, time.max, tzinfo=timezone.get_current_timezone())

    week_completed = Task.objects.filter(
        assigned_to=user,
        status='completed',
        updated_at__range=[start_datetime, end_datetime]
    ).count()
    week_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__range=[start_of_week, today]).count()
    week_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__range=[start_of_week, today]).count()

    month_completed = Task.objects.filter(assigned_to=user, status='completed', updated_at__month=today.month).count()
    month_cancelled = Task.objects.filter(assigned_to=user, status='cancelled', updated_at__month=today.month).count()
    month_in_progress = Task.objects.filter(assigned_to=user, status='in_progress', updated_at__month=today.month).count()

    return Response({
        "today_completed": today_completed,
        "today_cancelled": today_cancelled,
        "today_in_progress": today_in_progress,
        "week_completed": week_completed,
        "week_cancelled": week_cancelled,
        "week_in_progress": week_in_progress,
        "month_completed": month_completed,
        "month_cancelled": month_cancelled,
        "month_in_progress": month_in_progress
    }, status=status.HTTP_200_OK)