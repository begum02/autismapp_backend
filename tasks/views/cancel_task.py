from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_task_view(request, task_id):
    """
    Görevi iptal et
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Görev bulunamadı'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Yetki kontrolü
    if task.assigned_to != request.user and task.created_by != request.user and not request.user.is_staff:
        return Response(
            {'error': 'Bu görevi iptal etme yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if task.status == 'completed':
        return Response(
            {'error': 'Tamamlanmış görevler iptal edilemez'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    task.status = 'cancelled'
    task.save()
    
    print(f'✅ Görev iptal edildi: {task.title}')
    
    serializer = TaskSerializer(task)
    return Response(
        {
            "message": "Görev iptal edildi",
            "task": serializer.data
        },
        status=status.HTTP_200_OK
    )