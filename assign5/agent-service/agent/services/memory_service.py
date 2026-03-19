"""
agent/services/memory_service.py
────────────────────────────────────────────────────────────────
Module 3 – Memory / State Management

Cung cấp hai helper để đọc/ghi lịch sử hội thoại từ database:
  • get_chat_history()   – Lấy N tin nhắn gần nhất của một session.
  • save_chat_message()  – Lưu một tin nhắn mới vào lịch sử.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_chat_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Lấy tối đa `limit` tin nhắn gần nhất của phiên `session_id`.

    Args:
        session_id: Định danh phiên làm việc (UUID hoặc chuỗi bất kỳ).
        limit:      Số tin nhắn tối đa cần lấy (mặc định 10).

    Returns:
        Mảng các object theo chuẩn OpenAI messages:
        [{"role": "user"|"assistant", "content": "..."}, ...]
        Trả về [] nếu session chưa có lịch sử hoặc gặp lỗi.
    """
    # Import lazy để tránh circular import khi file được load sớm
    from agent.models import ChatMessage

    try:
        # Lấy `limit` bản tin mới nhất rồi đảo lại thứ tự cũ-trước-mới-sau
        queryset = (
            ChatMessage.objects
            .filter(session_id=session_id)
            .order_by("-created_at")[:limit]
        )
        messages = list(reversed(list(queryset)))

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    except Exception as exc:
        logger.error("get_chat_history error (session=%s): %s", session_id, exc, exc_info=True)
        return []


def save_chat_message(session_id: str, role: str, content: str) -> None:
    """
    Lưu một tin nhắn mới vào lịch sử hội thoại.

    Args:
        session_id: Định danh phiên làm việc.
        role:       "user" hoặc "assistant".
        content:    Nội dung tin nhắn.
    """
    from agent.models import ChatMessage

    try:
        ChatMessage.objects.create(
            session_id=session_id,
            role=role,
            content=content,
        )
    except Exception as exc:
        logger.error(
            "save_chat_message error (session=%s, role=%s): %s",
            session_id, role, exc, exc_info=True,
        )
