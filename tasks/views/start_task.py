from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request, task_id):
    """
    Görevi başlat
    
    Sadece görev sahibi (created_by) veya görevin atandığı kişi (assigned_to) başlatabilir.
    """
    user = request.user
    
    task = get_object_or_404(Task, id=task_id)
    
    # Sadece görev sahibi veya görevin atandığı kişi başlatabilir
    if task.assigned_to != user and task.created_by != user:
        return Response(
            {"detail": "Bu görevi başlatma yetkiniz yok. Sadece görev sahibi veya görevi atanan kişi başlatabilir."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Status kontrolü - sadece pending başlatılabilir
    if task.status != 'pending':
        return Response(
            {"detail": f"Sadece bekleyen görevler başlatılabilir. Mevcut durum: {task.get_status_display()}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Görevi başlat
    task.status = 'in_progress'
    task.save()
    
    return Response(
        {
            "message": "Görev başlatıldı! ▶️",
            "task": TaskSerializer(task).data
        },
        status=status.HTTP_200_OK
    )