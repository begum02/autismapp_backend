from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Kullanıcı profili
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Profil güncelleme
    """
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        print(f'✅ Profil güncellendi: {user.email}')
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    print(f'❌ Profil güncelleme hatası: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)