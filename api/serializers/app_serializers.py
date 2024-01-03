from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

from accounts.models import *
from backend.models import *


class AppSerializer(serializers.ModelSerializer):

    created_at = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    created_user = serializers.SerializerMethodField()
    
    class Meta:
        model = App
        fields = [
            'app_id', 
            'name',
            'created_user',
            'created_at',
            'last_updated',
            'status',
        ]
    
    def get_created_at(self, obj):
        date = obj.created_at
        date_object = None
        if date:
            date_object = {
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'hour': date.hour,
                'minute': date.minute,
                'second': date.second,
                'timezone': timezone.get_current_timezone_name()
            }
        return date_object

    def get_last_updated(self, obj):
        date = obj.last_updated
        date_object = None
        if date:
            date_object = {
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'hour': date.hour,
                'minute': date.minute,
                'second': date.second,
                'timezone': timezone.get_current_timezone_name()
            }
        return date_object
    
    def get_created_user(self, obj):
        if obj.created_user:
            return obj.created_user.email
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove fields with null values or empty strings
        return {key: value for key, value in data.items() if value is not None and value != ""}