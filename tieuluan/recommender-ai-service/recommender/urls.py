from django.urls import path
from .views import (
    AIChatView,
    AIEventIngestView,
    AIHealthView,
    AIKnowledgeRebuildView,
    CachedRecommendationsView,
    RecommendationsView,
)

urlpatterns = [
    path("ai/health/", AIHealthView.as_view(), name="ai-health"),
    path("ai/events/", AIEventIngestView.as_view(), name="ai-event-ingest"),
    path("ai/kb/rebuild/", AIKnowledgeRebuildView.as_view(), name="ai-kb-rebuild"),
    path("ai/recommendations/<int:customer_id>/", RecommendationsView.as_view(), name="ai-recommendations"),
    path("ai/recommendations/<int:customer_id>/cached/", CachedRecommendationsView.as_view(), name="ai-recommendations-cached"),
    path("ai/chat/", AIChatView.as_view(), name="ai-chat"),
    path("recommendations/<int:customer_id>/", RecommendationsView.as_view(), name="recommendations"),
    path("recommendations/<int:customer_id>/cached/", CachedRecommendationsView.as_view(), name="recommendations-cached"),
]
