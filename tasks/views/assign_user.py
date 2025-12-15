from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Task
from ..serializers import TaskSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignable_users(request):
    """
    Sorumlu kişinin atayabileceği kullanıcılar listesi
    """
    current_user = request.user
    
    # Eğer sorumlu kişiyse, destek gereksinimli kullanıcıları göster
    if current_user.role == 'responsible_person':
        users = User.objects.filter(
            role='support_required_individual'
        ).values('id', 'email', 'username', 'full_name', 'profile_picture', 'role')
        
        return Response({
            'count': len(users),
            'results': list(users)
        })
    
    return Response({'count': 0, 'results': []})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_user_view(request, task_id):
    """
    Görevi kullanıcıya ata
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Görev bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
    
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({'error': 'Kullanıcı ID gerekli'}, status=status.HTTP_400_BAD_REQUEST)
    
    task.assigned_to_id = user_id
    task.save()
    
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)