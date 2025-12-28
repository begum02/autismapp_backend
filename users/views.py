from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserSerializer, LoginSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Kullanıcı kaydı
    
    Body:
    {
        "email": "user@example.com",
        "username": "username",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+905551234567",
        "date_of_birth": "1990-01-01",
        "user_type": "individual",  // individual, support_required, responsible
        "responsible_role": "parent",  // Sadece user_type=responsible ise
        "password": "password123",
        "password_confirm": "password123"
    }
    """
    serializer = UserRegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # JWT token oluştur
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Kullanıcı başarıyla oluşturuldu",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Kullanıcı girişi (Email + Password)
    
    Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = serializer.get_tokens(user)
        
        return Response({
            "message": "Giriş başarılı",
            "user": UserSerializer(user).data,
            "tokens": tokens
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Kullanıcı çıkışı (Refresh token'ı blacklist'e ekle)
    
    Body:
    {
        "refresh": "refresh_token_here"
    }
    """
    try:
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token gereklidir"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()  # Token'ı blacklist'e ekle (simplejwt özelliği)
        
        return Response(
            {"message": "Çıkış başarılı"}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": "Geçersiz token"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Giriş yapmış kullanıcının profil bilgilerini döndür
    
    Headers:
    Authorization: Bearer {access_token}
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Kullanıcı profil güncelleme
    
    Headers:
    Authorization: Bearer {access_token}
    
    Body (güncellenecek alanlar):
    {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone": "+905551234567",
        "date_of_birth": "1990-01-01"
    }
    """
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Profil güncellendi",
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Şifre değiştirme
    
    Headers:
    Authorization: Bearer {access_token}
    
    Body:
    {
        "old_password": "old_password123",
        "new_password": "new_password123",
        "new_password_confirm": "new_password123"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    # Validations
    if not old_password or not new_password or not new_password_confirm:
        return Response(
            {"error": "Tüm alanlar gereklidir"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != new_password_confirm:
        return Response(
            {"error": "Yeni şifreler eşleşmiyor"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {"error": "Şifre en az 8 karakter olmalıdır"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Eski şifre kontrolü
    if not user.check_password(old_password):
        return Response(
            {"error": "Eski şifre hatalı"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Şifre güncelle
    user.set_password(new_password)
    user.save()
    
    return Response(
        {"message": "Şifre başarıyla değiştirildi"}, 
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    Kullanıcı listesi (sadece admin veya responsible person için)
    
    Query params:
    - user_type: individual, support_required, responsible
    - search: email, username, first_name, last_name
    """
    # Sadece staff veya responsible person görebilir
    if not (request.user.is_staff or request.user.user_type == 'responsible'):
        return Response(
            {"error": "Bu işlem için yetkiniz yok"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all()
    
    # Filtreleme
    user_type = request.query_params.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Arama
    search = request.query_params.get('search')
    if search:
        users = users.filter(
            email__icontains=search
        ) | users.filter(
            username__icontains=search
        ) | users.filter(
            first_name__icontains=search
        ) | users.filter(
            last_name__icontains=search
        )
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """
    Belirli bir kullanıcının detaylarını görüntüle
    
    URL: /api/users/{user_id}/
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Sadece kendi profilini veya staff görebilir
        if request.user.id != user_id and not request.user.is_staff:
            return Response(
                {"error": "Bu kullanıcıyı görüntüleme yetkiniz yok"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {"error": "Kullanıcı bulunamadı"}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Hesap silme (kendi hesabını)
    
    Headers:
    Authorization: Bearer {access_token}
    
    Body:
    {
        "password": "password123",
        "confirm": "DELETE"
    }
    """
    user = request.user
    password = request.data.get('password')
    confirm = request.data.get('confirm')
    
    # Validations
    if not password or confirm != 'DELETE':
        return Response(
            {"error": "Şifre ve 'DELETE' onayı gereklidir"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(password):
        return Response(
            {"error": "Şifre hatalı"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Hesabı sil (soft delete - is_active=False yapabilirsiniz)
    user.delete()  # Hard delete
    # veya: user.is_active = False; user.save()  # Soft delete
    
    return Response(
        {"message": "Hesap başarıyla silindi"}, 
        status=status.HTTP_200_OK
    )
