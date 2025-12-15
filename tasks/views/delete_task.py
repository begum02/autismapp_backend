from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task_view(request, task_id):
    """
    Görevi sil
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
            {"error": "Bu görevi silme yetkiniz yok"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    task_title = task.title
    task.delete()
    
    print(f'✅ Görev silindi: {task_title}')
    
    return Response(
        {"message": "Görev başarıyla silindi"},
        status=status.HTTP_204_NO_CONTENT
    )