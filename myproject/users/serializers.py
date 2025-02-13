from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from myproject import settings




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom fields
        user = self.user
        data['username'] = user.username
        data['photo'] = None
        data['is_admin'] = user.is_staff
        data['id'] = user.id
        data['is_premium'] = user.is_premium
        if user.photo:
            data['photo'] = f"{self.context['request'].build_absolute_uri(settings.MEDIA_URL)}{user.photo.name}"
        return data



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        # Authenticate the user
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        attrs['user'] = user
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only = True)
    password2 = serializers.CharField(write_only = True)
    is_admin = serializers.BooleanField(source='is_staff', read_only=True) 
    is_premium = serializers.BooleanField(read_only=True) 
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2', 'is_admin', 'is_premium']

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError('Passwords dont match')
        return attrs
    
    def create(self, validated_data):
        user = get_user_model()(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'photo', 'data_birth', 'is_premium']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.data_birth = validated_data.get('data_birth', instance.data_birth)
        instance.is_premium = validated_data.get('is_premium', instance.is_premium)
        instance.save()
        return instance
    

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError("New password must be different from the old password.")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()