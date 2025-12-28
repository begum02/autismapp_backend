from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Task
from .serializers import TaskSerializer, TaskCompletionSerializer

User = get_user_model()


# ==================== YETKİ KONTROLÜ (Helper Function) ====================

def check_task_permission(user, task, action='view'):
    """
    Görev üzerinde yetki kontrolü
    
    Args:
        user: İstek yapan kullanıcı
        task: Görev objesi
        action: 'view', 'edit', 'delete'
    
    Returns:
        (bool, str): (Yetki var mı?, Hata mesajı)
    """
    # Admin her şeyi yapabilir
    if user.is_staff:
        return True, None
    
    # Görev sahibi her şeyi yapabilir
    if task.user == user:
        return True, None
    
    # Görevi oluşturan kişi (sorumlu) düzenleyebilir/silebilir
    if task.created_by == user:
        # Sorumlu kişi mi kontrol et
        if user.user_type != 'responsible':
            return False, "Sadece sorumlu kişiler başkalarının görevlerini yönetebilir"
        
        # Hala bu bireyi yönetiyor mu?
        from users.models import SupportRelationship
        is_managing = SupportRelationship.objects.filter(
            responsible=user,
            support_required=task.user,
            is_verified=True
        ).exists()
        
        if not is_managing:
            return False, "Artık bu bireyi yönetme yetkiniz yok"
        
        return True, None
    
    return False, "Bu görevi görüntüleme/düzenleme yetkiniz yok"


# ==================== GÖREV OLUŞTURMA ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """
    Görev oluştur
    
    Body: {
        "user": 2,  // Opsiyonel: Sorumlu ise yönettiği bireyin ID'si
        "title": "Dişlerini Fırçala",
        "description": "Sabah kahvaltıdan sonra",
        "task_type": "daily_routine",
        "category": "hygiene",
        "date": "2025-12-03",
        "start_time": "09:00",
        "end_time": "09:10",
        "priority": "high",
        "difficulty_level": "easy"
    }
    """
    user = request.user
    task_data = request.data.copy()
    
    # Hedef kullanıcı (görev kime atanacak?)
    target_user_id = task_data.get('user', user.id)
    
    # Kendisi için mi oluşturuyor?
    if target_user_id == user.id:
        task_data['user'] = user.id
        task_data['created_by'] = user.id
    else:
        # Başkası için oluşturuyor - Sorumlu kişi olmalı
        if user.user_type != 'responsible':
            return Response(
                {"error": "Sadece sorumlu kişiler başkaları için görev oluşturabilir"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Yönettiği bireylerden mi kontrol et
        from users.models import SupportRelationship
        is_managing = SupportRelationship.objects.filter(
            responsible=user,
            support_required_id=target_user_id,
            is_verified=True
        ).exists()
        
        if not is_managing:
            return Response(
                {"error": "Bu bireyi yönetme yetkiniz yok"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task_data['user'] = target_user_id
        task_data['created_by'] = user.id
    
    # Görev oluştur
    serializer = TaskSerializer(data=task_data)
    if serializer.is_valid():
        task = serializer.save()
        return Response(
            {
                "message": "Görev başarıyla oluşturuldu",
                "task": TaskSerializer(task).data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== GÖREV LİSTELEME ====================

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


# ==================== GÖREV DETAY ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    """Görev detayı"""
    user = request.user
    
    try:
        task = Task.objects.select_related('user', 'created_by').get(id=task_id)
        
        # Yetki kontrolü
        has_permission, error_msg = check_task_permission(user, task, 'view')
        if not has_permission:
            return Response(
                {"error": error_msg},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı"},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== GÖREV GÜNCELLEME ====================

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    """Görev güncelleme"""
    user = request.user
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Yetki kontrolü
        has_permission, error_msg = check_task_permission(user, task, 'edit')
        if not has_permission:
            return Response(
                {"error": error_msg},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # user ve created_by değiştirilemez
        request_data = request.data.copy()
        request_data.pop('user', None)
        request_data.pop('created_by', None)
        
        serializer = TaskSerializer(task, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Görev güncellendi",
                "task": serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı"},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== GÖREV SİLME ====================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    """Görev silme - Sadece oluşturan kişi silebilir"""
    user = request.user
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Silme yetkisi kontrolü
        if not user.is_staff and task.created_by != user:
            return Response(
                {"error": "Bu görevi silme yetkiniz yok. Sadece görevi oluşturan kişi silebilir."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Sorumlu kişi hala yönetiyor mu?
        if user.user_type == 'responsible' and task.created_by == user:
            from users.models import SupportRelationship
            is_managing = SupportRelationship.objects.filter(
                responsible=user,
                support_required=task.user,
                is_verified=True
            ).exists()
            
            if not is_managing:
                return Response(
                    {"error": "Artık bu bireyi yönetme yetkiniz olmadığı için görevi silemezsiniz"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        task_title = task.title
        task.delete()
        
        return Response(
            {"message": f"'{task_title}' görevi silindi"},
            status=status.HTTP_200_OK
        )
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı"},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== GÖREV İPTAL ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_task(request, task_id):
    """Görevi iptal et"""
    user = request.user
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Yetki kontrolü
        has_permission, error_msg = check_task_permission(user, task, 'edit')
        if not has_permission:
            return Response(
                {"error": error_msg},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if task.status == 'completed':
            return Response(
                {"error": "Tamamlanmış görev iptal edilemez"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'cancelled'
        task.save()
        
        return Response({
            "message": "Görev iptal edildi",
            "task": TaskSerializer(task).data
        })
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı"},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== GÖREV TAMAMLAMA ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request, task_id):
    """
    Görevi tamamla - Sadece görev sahibi tamamlayabilir
    
    Body: {
        "notes": "Başarıyla tamamlandı",
        "rating": 5
    }
    """
    user = request.user
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Sadece görev sahibi tamamlayabilir
        if task.user != user:
            return Response(
                {"error": "Sadece görev sahibi görevi tamamlayabilir"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if task.status == 'completed':
            return Response(
                {"error": "Bu görev zaten tamamlanmış"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TaskCompletionSerializer(data=request.data)
        if serializer.is_valid():
            task.status = 'completed'
            task.completed_at = timezone.now()
            if serializer.validated_data.get('notes'):
                task.notes = serializer.validated_data['notes']
            task.save()
            
            return Response({
                "message": "Görev tamamlandı! 🎉",
                "task": TaskSerializer(task).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request, task_id):
    """Görevi başlat - Sadece görev sahibi başlatabilir"""
    user = request.user
    
    try:
        task = Task.objects.get(id=task_id, user=user)
        
        if task.status == 'completed':
            return Response(
                {"error": "Tamamlanmış görev başlatılamaz"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if task.status == 'cancelled':
            return Response(
                {"error": "İptal edilmiş görev başlatılamaz"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'in_progress'
        task.save()
        
        return Response({
            "message": "Görev başlatıldı",
            "task": TaskSerializer(task).data
        })
        
    except Task.DoesNotExist:
        return Response(
            {"error": "Görev bulunamadı veya size ait değil"},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== İSTATİSTİKLER ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    """
    Kullanıcının görev istatistikleri
    
    Query params:
    - period: today, week, month, all (default: all)
    """
    user = request.user
    period = request.query_params.get('period', 'all')
    
    tasks = Task.objects.filter(user=user)
    
    # Dönem filtresi
    if period == 'today':
        tasks = tasks.filter(date=timezone.now().date())
    elif period == 'week':
        from datetime import timedelta
        week_ago = timezone.now().date() - timedelta(days=7)
        tasks = tasks.filter(date__gte=week_ago)
    elif period == 'month':
        from datetime import timedelta
        month_ago = timezone.now().date() - timedelta(days=30)
        tasks = tasks.filter(date__gte=month_ago)
    
    # İstatistikler
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    cancelled_tasks = tasks.filter(status='cancelled').count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return Response({
        "period": period,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "cancelled_tasks": cancelled_tasks,
        "completion_rate": round(completion_rate, 2),
        "by_category": {
            "hygiene": tasks.filter(category='hygiene').count(),
            "education": tasks.filter(category='education').count(),
            "social": tasks.filter(category='social').count(),
            "health": tasks.filter(category='health').count(),
            "entertainment": tasks.filter(category='entertainment').count(),
            "other": tasks.filter(category='other').count(),
        }
    })
