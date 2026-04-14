from django.contrib import admin
from .models import BehaviorEvent, ChatMessage, GraphEdge, GraphNode, KnowledgeDocument, Recommendation

admin.site.register(Recommendation)
admin.site.register(BehaviorEvent)
admin.site.register(GraphNode)
admin.site.register(GraphEdge)
admin.site.register(KnowledgeDocument)
admin.site.register(ChatMessage)
