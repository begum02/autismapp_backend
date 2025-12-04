from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """Kullanıcı listesi (sadece responsible_person için)"""
    if request.user.role != 'responsible_person':
        return Response({
            'error': 'Bu işlem için yetkiniz yok'
        }, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """Kullanıcı detayı"""
    try:
        user = User.objects.get(id=user_id)
        
        # Sadece kendi profilini veya responsible_person görebilir
        if request.user.id != user_id and request.user.role != 'responsible_person':
            return Response({
                'error': 'Bu işlem için yetkiniz yok'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': 'Kullanıcı bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Hesap silme"""
    user = request.user
    user.is_active = False
    user.save()
    
    return Response({
        'message': 'Hesabınız devre dışı bırakıldı'
    }, status=status.HTTP_200_OK)