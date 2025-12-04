from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    """
    Görevi sil
    
    Sadece görev sahibi (created_by) veya görevin atandığı kişi (assigned_to) silebilir.
    """
    user = request.user
    
    task = get_object_or_404(Task, id=task_id)
    
    # Sadece görev sahibi veya görevin atandığı kişi silebilir
    if task.assigned_to != user and task.created_by != user:
        return Response(
            {"detail": "Bu görevi silme yetkiniz yok. Sadece görev sahibi veya görevi atanan kişi silebilir."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    task.delete()
    
    return Response(
        {"message": "Görev başarıyla silindi"},
        status=status.HTTP_204_NO_CONTENT
    )