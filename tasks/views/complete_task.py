from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task_view(request, task_id):
    """
    Görevi tamamla
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
            {"error": "Bu görevi tamamlama yetkiniz yok"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Status kontrolü
    if task.status == 'completed':
        return Response(
            {"error": "Bu görev zaten tamamlanmış"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if task.status == 'cancelled':
        return Response(
            {"error": "İptal edilmiş görev tamamlanamaz"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Görevi tamamla
    task.status = 'completed'
    task.save()
    
    print(f'✅ Görev tamamlandı: {task.title}')
    
    return Response(
        {
            "message": "Görev başarıyla tamamlandı! 🎉",
            "task": TaskSerializer(task).data
        },
        status=status.HTTP_200_OK
    )