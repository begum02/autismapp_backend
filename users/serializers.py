from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 
            'username', 
            'full_name', 
            'role',
            'password', 
            'password_confirm',
        ]
        extra_kwargs = {
            'role': {'required': True},
        }
    
    def validate(self, attrs):
        """Validation"""
        print(f"📝 Serializer validate - Gelen data: {attrs}")
        
        # Şifre kontrolü
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor"})
        
        # password_confirm'i kaldır
        attrs.pop('password_confirm')
        
        # Role kontrolü
        valid_roles = ['individual', 'support_required_individual', 'responsible_person']
        role = attrs.get('role')
        
        print(f"🔍 Frontend'den gelen role: {role}")
        
        if role not in valid_roles:
            raise serializers.ValidationError({
                'role': f"Geçersiz role. Geçerli değerler: {', '.join(valid_roles)}"
            })
        
        print(f"✅ Validate başarılı - Role: {role}")
        
        return attrs
    
    def create(self, validated_data):
        """User oluştur"""
        print(f"📝 Create ediliyor - validated_data: {validated_data}")
        print(f"📝 Role: {validated_data.get('role')}")
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            full_name=validated_data.get('full_name', ''),
            role=validated_data['role'],
            password=validated_data['password']
        )
        
        print(f"✅ User oluşturuldu - ID: {user.id}, Role: {user.role}, Email: {user.email}")
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'full_name', 'role', 'profile_picture', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class LoginSerializer(serializers.Serializer):
    """Login serializer - Email veya Username ile giriş"""
    email = serializers.CharField(required=True)  # ✅ Email veya username buraya gelecek
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        """Email veya username ile giriş kontrolü"""
        email_or_username = attrs.get('email', '').strip()
        password = attrs.get('password', '')
        
        print(f"🔍 Login validation - Email/Username: {email_or_username}")
        
        if not email_or_username:
            raise serializers.ValidationError({'email': 'Email veya kullanıcı adı gereklidir'})
        
        if not password:
            raise serializers.ValidationError({'password': 'Şifre gereklidir'})
        
        # ✅ Email mi yoksa username mi kontrol et
        user = None
        
        if '@' in email_or_username:
            # Email ile giriş
            try:
                user = User.objects.get(email__iexact=email_or_username)
                print(f"✅ User email ile bulundu: {user.email}")
            except User.DoesNotExist:
                print(f"❌ User email ile bulunamadı: {email_or_username}")
        else:
            # Username ile giriş
            try:
                user = User.objects.get(username__iexact=email_or_username)
                print(f"✅ User username ile bulundu: {user.username} ({user.email})")
            except User.DoesNotExist:
                print(f"❌ User username ile bulunamadı: {email_or_username}")
        
        # User bulunamadıysa hata
        if not user:
            raise serializers.ValidationError({'detail': 'Email/Kullanıcı adı veya şifre hatalı'})
        
        # Şifre kontrolü
        if not user.check_password(password):
            print(f"❌ Şifre yanlış")
            raise serializers.ValidationError({'detail': 'Email/Kullanıcı adı veya şifre hatalı'})
        
        # Aktif mi?
        if not user.is_active:
            print(f"❌ User aktif değil: {user.email}")
            raise serializers.ValidationError({'detail': 'Hesap aktif değil'})
        
        print(f"✅ Login validation başarılı - User: {user.email}, Role: {user.role}")
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({"new_password": "Şifreler eşleşmiyor"})
        return attrs