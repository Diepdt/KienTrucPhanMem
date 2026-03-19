from django.urls import path
from .views import AgentChatView, AgentHistoryView

urlpatterns = [
    path("agent/chat/",               AgentChatView.as_view(),    name="agent-chat"),
    path("agent/history/<str:session_id>/", AgentHistoryView.as_view(), name="agent-history"),
]
