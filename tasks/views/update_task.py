from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    """
    Görevi güncelle
    
    Sadece görev sahibi (created_by) veya görevin atandığı kişi (assigned_to) güncelleyebilir.
    """
    user = request.user
    
    task = get_object_or_404(Task, id=task_id)
    
    # Sadece görev sahibi veya görevin atandığı kişi güncelleyebilir
    if task.assigned_to != user and task.created_by != user:
        return Response(
            {"detail": "Bu görevi güncelleme yetkiniz yok. Sadece görev sahibi veya görevi atanan kişi güncelleyebilir."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Tamamlanmış görevler güncellenemez
    if task.status == 'completed':
        return Response(
            {"detail": "Tamamlanmış görevler güncellenemez"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = TaskSerializer(task, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Görev başarıyla güncellendi",
                "task": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)