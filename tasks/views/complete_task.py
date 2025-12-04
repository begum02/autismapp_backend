from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request, task_id):
    """
    Görevi tamamla
    
    Sadece görev sahibi (created_by) veya görevin atandığı kişi (assigned_to) tamamlayabilir.
    """
    user = request.user
    
    task = get_object_or_404(Task, id=task_id)
    
    # Sadece görev sahibi veya görevin atandığı kişi tamamlayabilir
    if task.assigned_to != user and task.created_by != user:
        return Response(
            {"detail": "Bu görevi tamamlama yetkiniz yok. Sadece görev sahibi veya görevi atanan kişi tamamlayabilir."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Status kontrolü
    if task.status == 'completed':
        return Response(
            {"detail": "Bu görev zaten tamamlanmış"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if task.status == 'cancelled':
        return Response(
            {"detail": "İptal edilmiş görev tamamlanamaz"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Görevi tamamla
    task.status = 'completed'
    task.save()
    
    return Response(
        {
            "message": "Görev başarıyla tamamlandı! 🎉",
            "task": TaskSerializer(task).data
        },
        status=status.HTTP_200_OK
    )