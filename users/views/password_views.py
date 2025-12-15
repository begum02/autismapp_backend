from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Şifre değiştirme
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            'error': 'Eski ve yeni şifre gereklidir'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Eski şifre hatalı'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    print(f'✅ Şifre değiştirildi: {user.email}')
    
    return Response({
        'message': 'Şifre başarıyla değiştirildi'
    }, status=status.HTTP_200_OK)