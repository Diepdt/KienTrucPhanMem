from rest_framework import serializers
from .models import Manager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'name', 'email', 'phone', 'is_active', 'created_at']

class ManagerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Manager
        fields = ['id', 'name', 'email', 'password', 'phone']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        mgr = Manager(**validated_data)
        mgr.set_password(raw_password)
        mgr.save()
        return mgr

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
