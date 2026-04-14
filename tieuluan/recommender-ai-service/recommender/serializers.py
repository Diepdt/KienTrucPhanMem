from rest_framework import serializers

from .models import BehaviorEvent, Recommendation


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


class RecommendationSerializer(serializers.ModelSerializer):
    confidence = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["service_type", "product_id", "score", "reason", "confidence", "product_name"]

    def get_confidence(self, obj):
        return obj.metadata.get("confidence") if isinstance(obj.metadata, dict) else None

    def get_product_name(self, obj):
        return obj.metadata.get("product_name") if isinstance(obj.metadata, dict) else ""


class ChatRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=1)
    message = serializers.CharField(max_length=2000)
    conversation_id = serializers.CharField(max_length=120, required=False, allow_blank=True)
