from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import UserSerializer, LoginSerializer, UserRegisterSerializer  # ✅ RegisterSerializer değil UserRegisterSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Kullanıcı kaydı
    """
    print('📝 Register isteği alındı')
    
    serializer = UserRegisterSerializer(data=request.data)  # ✅ Değişti
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Token oluştur
        refresh = RefreshToken.for_user(user)
        
        print(f'✅ Kullanıcı kaydedildi: {user.email}')
        
        return Response({
            'message': 'Kullanıcı başarıyla oluşturuldu',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    print(f'❌ Validation hatası: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Kullanıcı girişi
    """
    print(f'🔐 Login isteği alındı - Email/Username: {request.data.get("email")}')
    
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Token oluştur
        refresh = RefreshToken.for_user(user)
        
        print(f'✅ Login başarılı - User: {user.email}, Role: {user.role}')
        
        return Response({
            'message': 'Giriş başarılı',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    print(f'❌ Login validation hatası: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Kullanıcı çıkışı
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        print(f'✅ Logout başarılı - User: {request.user.email}')
        
        return Response({
            'message': 'Çıkış başarılı'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f'❌ Logout hatası: {str(e)}')
        return Response({
            'error': 'Çıkış yapılırken bir hata oluştu'
        }, status=status.HTTP_400_BAD_REQUEST)