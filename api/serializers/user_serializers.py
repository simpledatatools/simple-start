from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

from accounts.models import *
from backend.models import *


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'name', 'profile_photo']

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

    def get_profile_photo(self, obj):
        profile_photo = obj.profile_photo
        url = None
        if profile_photo:
            url = profile_photo.file.url
        return url
    

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'token', 'profile_photo']
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_id(self, obj):
        return obj.id

    def get_profile_photo(self, obj):
        profile_photo = obj.profile_photo
        url = None
        if profile_photo:
            url = profile_photo.file.url
        return url