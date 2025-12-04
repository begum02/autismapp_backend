from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from tasks.models import Task
from tasks.serializers import TaskSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    """
    Görev detayı görüntüleme
    """
    try:
        task = Task.objects.get(id=task_id)
        
        # Yetki kontrolü
        if task.assigned_to != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Bu görevi görüntüleme yetkiniz yok'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Task.DoesNotExist:
        return Response(
            {'error': 'Görev bulunamadı'},
            status=status.HTTP_404_NOT_FOUND
        )