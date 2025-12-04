from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import SupportRelationship

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'username',
            'email', 
            'full_name', 
            'role', 
            'profile_picture',
            'date_joined',
            'last_login',
            'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username',
            'email', 
            'password', 
            'password_confirm', 
            'full_name', 
            'role'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor"})
        return data
    
    def validate_username(self, value):
        """Username benzersizliğini kontrol et"""
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu kullanıcı adı zaten kullanılıyor")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email adresi zaten kullanılıyor")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            password=password,
            full_name=validated_data.get('full_name', ''),
            role=validated_data.get('role', 'individual')
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer - Email veya Username ile giriş yapılabilir
    """
    email_or_username = serializers.CharField(
        label="E-posta veya Kullanıcı Adı",
        help_text="E-posta adresi veya kullanıcı adı ile giriş yapabilirsiniz"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        if not email_or_username or not password:
            raise serializers.ValidationError("E-posta/kullanıcı adı ve şifre gereklidir")

        # Email mi username mi kontrol et
        user = None
        
        # Önce email olarak dene
        if '@' in email_or_username:
            try:
                user = User.objects.get(email=email_or_username)
            except User.DoesNotExist:
                pass
        
        # Email bulunamadıysa username olarak dene
        if not user:
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                pass
        
        # Kullanıcı bulunamadı
        if not user:
            raise serializers.ValidationError("E-posta/kullanıcı adı veya şifre hatalı")
        
        # Şifreyi kontrol et
        if not user.check_password(password):
            raise serializers.ValidationError("E-posta/kullanıcı adı veya şifre hatalı")
        
        # Kullanıcı aktif mi?
        if not user.is_active:
            raise serializers.ValidationError("Bu hesap devre dışı bırakılmış")
        
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Şifreler eşleşmiyor"})
        return data


class SupportRelationshipSerializer(serializers.ModelSerializer):
    responsible_person_name = serializers.CharField(
        source='responsible_person.full_name', 
        read_only=True
    )
    individual_name = serializers.CharField(
        source='individual.full_name', 
        read_only=True
    )
    
    class Meta:
        model = SupportRelationship
        fields = [
            'id',
            'responsible_person',
            'responsible_person_name',
            'individual',
            'individual_name',
            'relationship_type',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Aynı kişi hem sorumlu hem birey olamaz
        if data.get('responsible_person') == data.get('individual'):
            raise serializers.ValidationError("Sorumlu kişi ve birey aynı olamaz")
        
        # Sorumlu kişi role kontrolü
        if data.get('responsible_person') and data['responsible_person'].role != 'responsible_person':
            raise serializers.ValidationError({
                'responsible_person': 'Sorumlu kişi rolü "responsible_person" olmalıdır'
            })
        
        # Birey role kontrolü
        if data.get('individual') and data['individual'].role != 'support_required_individual':
            raise serializers.ValidationError({
                'individual': 'Birey rolü "support_required_individual" olmalıdır'
            })
        
        return data