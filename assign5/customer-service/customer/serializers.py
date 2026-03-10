from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address', 'is_active', 'created_at']

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'password', 'phone', 'address']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(raw_password)
        customer.save()
        return customer

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
