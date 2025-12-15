from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task_view(request, task_id):
    """
    Görevi başlat
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Görev bulunamadı'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Yetki kontrolü
    if task.assigned_to != request.user and task.created_by != request.user:
        return Response(
            {"error": "Bu görevi başlatma yetkiniz yok"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Status kontrolü - sadece pending başlatılabilir
    if task.status != 'pending':
        return Response(
            {"error": f"Sadece bekleyen görevler başlatılabilir. Mevcut durum: {task.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Görevi başlat
    task.status = 'in_progress'
    task.save()
    
    print(f'✅ Görev başlatıldı: {task.title}')
    
    return Response(
        {
            "message": "Görev başlatıldı! ▶️",
            "task": TaskSerializer(task).data
        },
        status=status.HTTP_200_OK
    )