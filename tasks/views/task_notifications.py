from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_notifications_view(request):
    """
    Kullanıcının yeni task bildirimlerini getir (Redis'den)
    """
    try:
        cache_key = f'new_task_{request.user.id}'
        new_task = cache.get(cache_key)
        
        if new_task:
            # Redis'den sil (bir kere okundu)
            cache.delete(cache_key)
            
            return Response({
                'has_new_task': True,
                'task': new_task
            }, status=status.HTTP_200_OK)
        
        return Response({
            'has_new_task': False,
            'task': None
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )