from rest_framework import serializers

from .models import BehaviorEvent


class BehaviorEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorEvent
        fields = [
            "customer_id",
            "event_type",
            "service_type",
            "product_id",
            "query_text",
            "payload",
        ]


class ChatRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=0)
    message = serializers.CharField(max_length=2000)
    conversation_id = serializers.CharField(max_length=120, required=False, allow_blank=True)
