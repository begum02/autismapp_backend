from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ..serializers import UserRegisterSerializer, UserSerializer, LoginSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Kullanıcı kaydı"""
    try:
        print(f"📝 Register isteği alındı - Email: {request.data.get('email')}")
        
        serializer = UserRegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'message': 'Kayıt başarılı',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
        
        print(f"✅ Register başarılı - User: {user.email}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ Register exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': f'Sunucu hatası: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Kullanıcı girişi"""
    try:
        print(f"🔐 Login isteği alındı - Email: {request.data.get('email')}")
        
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"❌ Validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Email ile kullanıcıyı bul
        try:
            user = User.objects.get(email=email)
            print(f"✅ User bulundu: {user.email}, Role: {user.role}")
        except User.DoesNotExist:
            print(f"❌ User bulunamadı: {email}")
            return Response(
                {'detail': 'Email veya şifre hatalı'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Şifreyi kontrol et
        if not user.check_password(password):
            print(f"❌ Şifre yanlış")
            return Response(
                {'detail': 'Email veya şifre hatalı'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            print(f"❌ Hesap aktif değil")
            return Response(
                {'detail': 'Hesap aktif değil'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # JWT Token oluştur
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'message': 'Giriş başarılı',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }
        
        print(f"✅ Login başarılı - Response keys: {response_data.keys()}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Login exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': f'Sunucu hatası: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Kullanıcı çıkışı"""
    try:
        print(f"🚪 Logout isteği alındı")
        
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token gerekli'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            print(f"✅ Token blacklist'e eklendi")
        except Exception as e:
            print(f"⚠️  Token blacklist hatası: {str(e)}")
            # Token zaten expire olmuş olabilir, hata vermeyelim
        
        return Response({
            'message': 'Çıkış başarılı'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Logout exception: {str(e)}")
        return Response({
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)