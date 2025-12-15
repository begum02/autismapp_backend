from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from ..serializers import TaskSerializer

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_task_view(request, task_id):
    """
    Görevi güncelle
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
            {"error": "Bu görevi güncelleme yetkiniz yok"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Tamamlanmış görevler güncellenemez
    if task.status == 'completed':
        return Response(
            {"error": "Tamamlanmış görevler güncellenemez"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = TaskSerializer(task, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        print(f'✅ Görev güncellendi: {task.title}')
        return Response(
            {
                "message": "Görev başarıyla güncellendi",
                "task": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)