"""
agent/models.py
────────────────────────────────────────────────────────────────
Lưu trữ lịch sử hội thoại của Agent theo session.
"""

from django.db import models


class ChatMessage(models.Model):
    """Một tin nhắn trong lịch sử hội thoại của một phiên làm việc."""

    ROLE_USER      = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES   = [
        (ROLE_USER,      "User"),
        (ROLE_ASSISTANT, "Assistant"),
    ]

    session_id = models.CharField(max_length=255, db_index=True)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes  = [models.Index(fields=["session_id", "created_at"])]

    def __str__(self) -> str:
        preview = self.content[:60].replace("\n", " ")
        return f"[{self.session_id}] {self.role}: {preview}"
