from django.db import models

from .assignment.config import EVENT_CHOICES


class BehaviorEvent(models.Model):
    """Raw user behavior events ingested from gateway/services."""

    customer_id = models.IntegerField(db_index=True)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES, db_index=True)
    service_type = models.CharField(max_length=50, blank=True, default="", db_index=True)
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    query_text = models.CharField(max_length=500, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class ChatMessage(models.Model):
    """Chat history storage for context-aware dialogue."""

    ROLES = [("user", "User"), ("assistant", "Assistant")]

    conversation_id = models.CharField(max_length=120, db_index=True)
    customer_id = models.IntegerField(db_index=True)
    role = models.CharField(max_length=20, choices=ROLES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
