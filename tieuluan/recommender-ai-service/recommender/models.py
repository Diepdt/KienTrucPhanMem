from django.db import models


class Recommendation(models.Model):
    """Recommendation cache for fast serving."""

    customer_id = models.IntegerField(db_index=True)
    service_type = models.CharField(max_length=50, default="book", db_index=True)
    product_id = models.IntegerField(db_index=True)
    score = models.FloatField(default=0.0)
    reason = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-score"]
        unique_together = ["customer_id", "service_type", "product_id"]

    def __str__(self):
        return f"Recommend {self.service_type}#{self.product_id} -> customer#{self.customer_id}"


class BehaviorEvent(models.Model):
    """Raw user behavior events ingested from gateway/services."""

    EVENT_TYPES = [
        ("search", "Search"),
        ("view", "View"),
        ("click", "Click"),
        ("add_to_cart", "Add To Cart"),
        ("purchase", "Purchase"),
        ("chat", "Chat"),
    ]

    customer_id = models.IntegerField(db_index=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    service_type = models.CharField(max_length=50, blank=True, default="", db_index=True)
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    query_text = models.CharField(max_length=500, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class GraphNode(models.Model):
    """Node in semantic behavior graph (User/Product/Category/Query)."""

    NODE_TYPES = [
        ("user", "User"),
        ("product", "Product"),
        ("category", "Category"),
        ("query", "Query"),
    ]

    node_type = models.CharField(max_length=20, choices=NODE_TYPES, db_index=True)
    external_id = models.CharField(max_length=120, db_index=True)
    label = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["node_type", "external_id"]

    def __str__(self):
        return f"{self.node_type}:{self.external_id}"


class GraphEdge(models.Model):
    """Weighted edge in semantic behavior graph."""

    source = models.ForeignKey(GraphNode, on_delete=models.CASCADE, related_name="out_edges")
    target = models.ForeignKey(GraphNode, on_delete=models.CASCADE, related_name="in_edges")
    relation = models.CharField(max_length=50, db_index=True)
    weight = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["source", "target", "relation"]
        indexes = [models.Index(fields=["relation", "weight"])]


class KnowledgeDocument(models.Model):
    """Document corpus for RAG retrieval."""

    source = models.CharField(max_length=60, db_index=True)
    service_type = models.CharField(max_length=50, blank=True, default="", db_index=True)
    external_id = models.CharField(max_length=120, blank=True, default="")
    title = models.CharField(max_length=255)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["source", "service_type"])]


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
