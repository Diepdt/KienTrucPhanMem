from rest_framework import serializers
from .models import Staff, StaffToken


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'phone', 'role', 'is_active', 'created_at']


class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'password', 'phone', 'role']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        staff = Staff(**validated_data)
        staff.set_password(raw_password)
        staff.save()
        return staff


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
