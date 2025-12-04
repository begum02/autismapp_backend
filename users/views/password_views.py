from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import ChangePasswordSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Şifre değiştirme"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        # Eski şifreyi kontrol et
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'Eski şifre hatalı'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Yeni şifreyi kaydet
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Şifre başarıyla değiştirildi'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)