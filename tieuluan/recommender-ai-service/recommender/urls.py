from django.urls import path
from .views import (
    AIChatView,
    AIEventIngestView,
    AIEventIngestAndRecommendView,
    AIHealthView,
    GraphRecommendationsView,
)

urlpatterns = [
    path("health/", AIHealthView.as_view(), name="ai-health"),
    path("events/", AIEventIngestView.as_view(), name="ai-event-ingest"),
    path("events/recommend/", AIEventIngestAndRecommendView.as_view(), name="ai-event-ingest-recommend"),
    path("recommendations/user/<int:customer_id>/", GraphRecommendationsView.as_view(), name="api-recommendations-user"),
    path("chat/", AIChatView.as_view(), name="ai-chat"),
]
