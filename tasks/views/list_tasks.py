from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model  # ← EKLENDİ
from tasks.models import Task  # ← DÜZELTİLDİ (. yerine tasks.)
from tasks.serializers import TaskSerializer  # ← DÜZELTİLDİ

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_tasks(request):
    """
    Kendi görevlerimi listele
    
    Query params:
    - date: YYYY-MM-DD
    - status: pending, in_progress, completed, cancelled
    - category: hygiene, education, social, health, other
    """
    user = request.user
    tasks = Task.objects.filter(user=user)
    
    # Filtreleme
    date_filter = request.query_params.get('date')
    if date_filter:
        tasks = tasks.filter(date=date_filter)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    category_filter = request.query_params.get('category')
    if category_filter:
        tasks = tasks.filter(category=category_filter)
    
    tasks = tasks.order_by('date', 'start_time')
    
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_managed_tasks(request):
    """
    Sorumlu kişi: Yönettiği bireylerin görevlerini listeler
    
    Query params:
    - individual_id: Belirli bir bireyin görevleri
    - date: YYYY-MM-DD
    - status: pending, in_progress, completed
    """
    user = request.user
    
    if user.user_type != 'responsible':
        return Response(
            {"error": "Sadece sorumlu kişiler erişebilir"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Yönettiği bireyler
    from users.models import SupportRelationship
    managed_individuals = User.objects.filter(
        support_relationships__responsible=user,
        support_relationships__is_verified=True
    )
    
    # Filtreleme
    individual_id = request.query_params.get('individual_id')
    if individual_id:
        managed_individuals = managed_individuals.filter(id=individual_id)
    
    # Görevleri getir
    tasks = Task.objects.filter(user__in=managed_individuals)
    
    date_filter = request.query_params.get('date')
    if date_filter:
        tasks = tasks.filter(date=date_filter)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    tasks = tasks.select_related('user', 'created_by').order_by('-date', 'start_time')
    
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list(request):
    """
    Görev listesi - filtreleme desteği ile
    """
    user = request.user
    tasks = Task.objects.filter(assigned_to=user)
    
    # Tarih filtresi
    date = request.query_params.get('date')
    if date:
        tasks = tasks.filter(scheduled_date=date)
    
    # Durum filtresi
    status_filter = request.query_params.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # assigned_to filtresi (sorumlu kişiler için)
    if user.role == 'responsible_person':
        assigned_to = request.query_params.get('assigned_to')
        if assigned_to:
            tasks = Task.objects.filter(assigned_to_id=assigned_to)
    
    tasks = tasks.order_by('scheduled_date', 'start_time')
    serializer = TaskSerializer(tasks, many=True)
    
    return Response({
        'count': tasks.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)