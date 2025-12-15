from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users_view(request):
    """
    Kullanıcı listesi
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, user_id):
    """
    Kullanıcı detayı
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': 'Kullanıcı bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    """
    Hesap silme
    """
    user = request.user
    user.delete()
    
    print(f'✅ Hesap silindi: {user.email}')
    
    return Response({
        'message': 'Hesap başarıyla silindi'
    }, status=status.HTTP_200_OK)