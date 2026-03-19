from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ("session_id", "role", "short_content", "created_at")
    list_filter   = ("role",)
    search_fields = ("session_id", "content")
    ordering      = ("-created_at",)
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:80]
    short_content.short_description = "Content"
