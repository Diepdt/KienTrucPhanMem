import logging
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .assignment.services import build_services
from .models import BehaviorEvent, ChatMessage
from .serializers import BehaviorEventSerializer, ChatRequestSerializer
from recommender.services.recommendation_service import RecommendationService
from recommender.services.chatbot_service import ChatbotService
from recommender.services.knowledge_graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)

neo4j_service, _ = build_services()

# service layer instances
kg_service = KnowledgeGraphService(
    uri=os.getenv("NEO4J_URI", ""), username=os.getenv("NEO4J_USER", ""), password=os.getenv("NEO4J_PASSWORD", "")
)
recommendation_service = RecommendationService(model_path=os.getenv("LSTM_MODEL_PATH"))
chatbot_service = ChatbotService(kg_service)


def _error_response(message: str, code=status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"success": False, "error": message}, status=code)


def _safe_top_k(raw_value, default=10, min_value=1, max_value=50) -> int:
    try:
        value = int(raw_value)
    except Exception:
        return default
    return max(min_value, min(value, max_value))


class AIHealthView(APIView):
    def get(self, request):
        return Response(
            {
                "service": "recommender-ai-service",
                "status": "ok",
                "scope": "assignment-a-b-c-d",
                "metrics": {
                    "events": BehaviorEvent.objects.count(),
                    "chat_messages": ChatMessage.objects.count(),
                },
                "architecture": ["rnn-lstm-bilstm", "neo4j-kb-graph", "graph-rag-chat"],
            }
        )


class AIEventIngestView(APIView):
    """Persist user behavior event for later model/graph usage."""

    def post(self, request):
        serializer = BehaviorEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.save()
        return Response({"success": True, "event_id": event.id}, status=status.HTTP_201_CREATED)


class AIEventIngestAndRecommendView(APIView):
    """Task d: save event and return recommended products for search/cart flows."""

    def post(self, request):
        serializer = BehaviorEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        try:
            # ingest into neo4j for graph knowledge
            neo4j_service.ingest_event(
                customer_id=event.customer_id,
                product_id=event.product_id,
                action=event.event_type,
                timestamp=event.created_at,
            )
            # get recommendations from LSTM-based recommender first, fallback to graph
            recs = recommendation_service.get_recommendations_for_user(event.customer_id, top_k=10)
            if not recs:
                recommendations = neo4j_service.recommend_products(event.customer_id, top_k=10)
            else:
                recommendations = recs
        except Exception:
            recommendations = []

        return Response(
            {
                "success": True,
                "event_id": event.id,
                "customer_id": event.customer_id,
                "recommendations": recommendations,
            }
        )


# Recommendation endpoint using LSTM inference
class GraphRecommendationsView(APIView):
    def get(self, request, customer_id):
        top_k = _safe_top_k(request.query_params.get("top_k", 10))
        try:
            result = recommendation_service.get_recommendations_for_user_with_meta(customer_id, top_k=top_k)
            recommendations = result.get("recommendations", [])
            source = result.get("source", "lstm_model")
            fallback_reason = result.get("fallback_reason")
        except Exception:
            recommendations = []
            source = "rule_based_fallback"
            fallback_reason = "inference_error"

        return Response(
            {
                "customer_id": customer_id,
                "total": len(recommendations),
                "recommendations": recommendations,
                "source": source,
                "fallback_reason": fallback_reason,
            }
        )


class AIChatView(APIView):
    """Graph-RAG chat with assignment module only."""

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            # use simplified chatbot service
            result = chatbot_service.chat(payload["customer_id"], payload["message"], top_k=8)

            # persist chat messages
            conv = payload.get("conversation_id") or f"conv-{payload['customer_id']}"
            ChatMessage.objects.create(conversation_id=conv, customer_id=payload["customer_id"], role="user", content=payload["message"])
            ChatMessage.objects.create(conversation_id=conv, customer_id=payload["customer_id"], role="assistant", content=result.get("reply", ""))

            return Response(result)
        except Exception as exc:
            logger.exception("AI chat failed: %s", exc)
            return _error_response("Internal server error", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
