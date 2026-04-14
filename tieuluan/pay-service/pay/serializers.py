from rest_framework import serializers
from .models import PaymentMethod, Payment

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description', 'is_active']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'method', 'method_name', 'amount',
                  'status', 'transaction_id', 'notes', 'created_at', 'updated_at']
