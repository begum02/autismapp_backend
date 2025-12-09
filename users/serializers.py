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
            'role',  # ✅ Frontend'den direkt role alacağız
            'password', 
            'password_confirm',
        ]
        extra_kwargs = {
            'role': {'required': True},  # ✅ Role zorunlu
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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email veya şifre hatalı')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Email veya şifre hatalı')
        
        if not user.is_active:
            raise serializers.ValidationError('Hesap aktif değil')
        
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