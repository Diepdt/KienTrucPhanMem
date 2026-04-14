import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai.behavior_engine import BehaviorRecommendationEngine
from .ai.constants import EVENT_WEIGHTS
from .ai.graph_engine import GraphKnowledgeEngine
from .ai.kb_builder import KnowledgeBaseBuilder
from .ai.rag_engine import RAGChatEngine
from .models import BehaviorEvent, ChatMessage, GraphEdge, GraphNode, KnowledgeDocument, Recommendation
from .serializers import BehaviorEventSerializer, ChatRequestSerializer, RecommendationSerializer

logger = logging.getLogger(__name__)

graph_engine = GraphKnowledgeEngine()
behavior_engine = BehaviorRecommendationEngine()
rag_engine = RAGChatEngine()
kb_builder = KnowledgeBaseBuilder()


class AIHealthView(APIView):
    def get(self, request):
        return Response(
            {
                "service": "recommender-ai-service",
                "status": "ok",
                "metrics": {
                    "events": BehaviorEvent.objects.count(),
                    "graph_nodes": GraphNode.objects.count(),
                    "graph_edges": GraphEdge.objects.count(),
                    "documents": KnowledgeDocument.objects.count(),
                    "cached_recommendations": Recommendation.objects.count(),
                    "chat_messages": ChatMessage.objects.count(),
                },
                "architecture": ["graph-knowledge", "behavior-learning", "rag-chat"],
            }
        )


class AIEventIngestView(APIView):
    """Ingest events and update behavior graph incrementally."""

    def post(self, request):
        serializer = BehaviorEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.save()

        # Weighted behavior edge: w = a*click + b*cart + c*purchase (+ view/search/chat)
        weight = float(EVENT_WEIGHTS.get(event.event_type, 1.0))
        if isinstance(event.payload, dict):
            clicks = float(event.payload.get("clicks", 0))
            carts = float(event.payload.get("carts", 0))
            purchases = float(event.payload.get("purchases", 0))
            if clicks or carts or purchases:
                weight = 1.0 * clicks + 2.5 * carts + 4.0 * purchases

        graph_engine.ingest_event(event=event, event_weight=weight)
        return Response({"success": True, "event_id": event.id, "edge_weight": weight}, status=status.HTTP_201_CREATED)


class AIKnowledgeRebuildView(APIView):
    """Rebuild document KB and graph from all events."""

    def post(self, request):
        kb_result = kb_builder.rebuild()
        graph_engine.rebuild_from_events()
        return Response(
            {
                "success": True,
                "kb": kb_result,
                "graph": {
                    "nodes": GraphNode.objects.count(),
                    "edges": GraphEdge.objects.count(),
                },
            }
        )


class RecommendationsView(APIView):
    def get(self, request, customer_id):
        top_k = int(request.query_params.get("top_k", 10))
        recommendations = behavior_engine.recommend(customer_id=customer_id, top_k=max(1, min(top_k, 50)))
        return Response(
            {
                "customer_id": customer_id,
                "total": len(recommendations),
                "recommendations": recommendations,
            }
        )


class CachedRecommendationsView(APIView):
    def get(self, request, customer_id):
        recs = Recommendation.objects.filter(customer_id=customer_id).order_by("-score")
        if not recs.exists():
            return RecommendationsView().get(request, customer_id)

        data = RecommendationSerializer(recs, many=True).data
        return Response({"customer_id": customer_id, "total": len(data), "recommendations": data})


class AIChatView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            result = rag_engine.chat(
                customer_id=payload["customer_id"],
                message=payload["message"],
                conversation_id=payload.get("conversation_id") or None,
            )
            return Response(result)
        except Exception as exc:
            logger.exception("AI chat failed: %s", exc)
            return Response({"success": False, "error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
