"""
agent/views.py
────────────────────────────────────────────────────────────────
Controller – Điểm vào HTTP duy nhất của AI Agent.

Endpoint:
  POST /api/agent/chat/
  Body JSON: { "message": str, "session_id": str, "user_id": int }
  Response:  { "reply": str, "session_id": str }

Vòng lặp thực thi (Function Calling Loop):
  a. Nạp lịch sử chat + gộp tin nhắn mới + SYSTEM_PROMPT.
  b. Gọi LLM lần 1 (kèm TOOL_DEFINITIONS).
  c. Nếu LLM trả về tool_calls → map & thực thi từng hàm.
  d. Nạp kết quả tool vào messages → gọi LLM lần 2 để tóm tắt.
  e. Lưu [user, assistant] vào memory → trả response cho client.
"""

import json
import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.llm_service import call_llm, extract_text_content, extract_tool_calls
from .services.memory_service import get_chat_history, save_chat_message
from .services.tool_service import TOOL_DEFINITIONS, TOOL_FUNCTION_MAP
from .utils.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AgentChatView(APIView):
    """
    Endpoint chính của AI Agent.

    Nhận tin nhắn từ client, chạy vòng lặp Function Calling với LLM
    (OpenAI GPT), thực thi công cụ nếu cần, và trả lời bằng văn bản.
    """

    def post(self, request: Request) -> Response:
        # ── Validate input ────────────────────────────────────────────────────
        user_message = (request.data.get("message") or "").strip()
        session_id   = (request.data.get("session_id") or "").strip()
        user_id      = request.data.get("user_id")

        if not user_message:
            return Response(
                {"error": "Trường 'message' không được để trống."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not session_id:
            return Response(
                {"error": "Trường 'session_id' không được để trống."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            final_reply = self._run_agent_loop(user_message, session_id, user_id)
        except RuntimeError as exc:
            logger.error("AgentChatView config/runtime error: %s", exc)
            fallback_reply = self._fallback_reply(user_message, user_id)
            save_chat_message(session_id, "user", user_message)
            save_chat_message(session_id, "assistant", fallback_reply)
            return Response({
                "reply": fallback_reply,
                "session_id": session_id,
                "fallback": True,
                "note": str(exc),
            })
        except Exception as exc:
            logger.error("AgentChatView unexpected error: %s", exc, exc_info=True)
            fallback_reply = self._fallback_reply(user_message, user_id)
            save_chat_message(session_id, "user", user_message)
            save_chat_message(session_id, "assistant", fallback_reply)
            return Response({
                "reply": fallback_reply,
                "session_id": session_id,
                "fallback": True,
            })

        return Response({"reply": final_reply, "session_id": session_id})

    # ── Private: vòng lặp thực thi ────────────────────────────────────────────

    def _run_agent_loop(self, user_message: str, session_id: str, user_id) -> str:
        """
        Vòng lặp Function Calling đầy đủ.

        Returns: chuỗi văn bản cuối cùng gửi lại cho client.
        """

        # ── Bước a: Nạp lịch sử & xây dựng danh sách messages ───────────────
        history  = get_chat_history(session_id, limit=10)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)

        # Gắn user_id vào context nếu có (dùng trong tool add_book_to_cart)
        effective_message = user_message
        if user_id is not None:
            # Thêm hint vào nội dung để LLM biết user_id khi gọi add_book_to_cart
            effective_message = (
                f"[user_id={user_id}] {user_message}"
            )
        messages.append({"role": "user", "content": effective_message})

        # ── Bước b: Gọi LLM lần 1 (kèm TOOL_DEFINITIONS) ────────────────────
        llm_response = call_llm(messages, tools=TOOL_DEFINITIONS)

        # ── Bước c: Kiểm tra có tool_calls không ─────────────────────────────
        tool_calls  = extract_tool_calls(llm_response)
        final_reply = ""

        if tool_calls:
            # Append tin nhắn assistant (chứa tool_calls) vào luồng
            assistant_raw_msg = llm_response["choices"][0]["message"]
            messages.append(assistant_raw_msg)

            # Thực thi lần lượt từng tool call
            for tc in tool_calls:
                tool_call_id = tc["id"]
                func_name    = tc["function"]["name"]

                try:
                    func_args = json.loads(tc["function"]["arguments"])
                except (json.JSONDecodeError, KeyError):
                    func_args = {}

                logger.info(
                    "Agent [session=%s] → tool=%s, args=%s",
                    session_id, func_name, func_args,
                )

                # Map tên hàm → callable & thực thi
                tool_fn = TOOL_FUNCTION_MAP.get(func_name)
                if tool_fn is not None:
                    tool_result = tool_fn(**func_args)
                else:
                    tool_result = json.dumps(
                        {"error": f"Tool '{func_name}' không được định nghĩa."},
                        ensure_ascii=False,
                    )

                logger.debug("Tool result [%s]: %s", func_name, tool_result[:200])

                # ── Bước d: Append kết quả tool vào messages (role=tool) ──────
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_call_id,
                    "content":      tool_result,
                })

            # Gọi LLM lần 2 để tóm tắt kết quả tool thành ngôn ngữ tự nhiên
            final_llm_response = call_llm(messages, tools=None)
            final_reply        = extract_text_content(final_llm_response)

        else:
            # LLM trả lời trực tiếp, không cần gọi tool
            final_reply = extract_text_content(llm_response)

        # ── Bước e: Lưu [user, assistant] vào memory ─────────────────────────
        save_chat_message(session_id, "user",      user_message)
        save_chat_message(session_id, "assistant", final_reply)

        return final_reply

    def _fallback_reply(self, user_message: str, user_id) -> str:
        """
        Fallback khi LLM provider lỗi: xử lý các thao tác cơ bản bằng tool nội bộ.
        """
        lowered = user_message.lower()

        # Intent: xem chi tiết sách theo book_id
        if any(keyword in lowered for keyword in [
            "chi tiết", "thông tin", "nội dung", "mô tả", "review", "đánh giá",
            "detail", "details", "info", "information", "description", "product"
        ]):
            import re
            match = re.search(r"(?:id\s*)?(\d+)", lowered)
            if match:
                book_id = int(match.group(1))
                detail_fn = TOOL_FUNCTION_MAP.get("get_book_detail")
                if detail_fn:
                    try:
                        result = detail_fn(book_id=book_id)
                        payload = json.loads(result)
                        if not payload.get("found"):
                            return payload.get("message") or payload.get("error") or "Không tìm thấy thông tin sách phù hợp."

                        book = payload.get("book", {})
                        reviews = payload.get("reviews", {})
                        lines = [
                            f"Thông tin sách ID {book.get('id')}",
                            f"- Tên: {book.get('title')}",
                            f"- Tác giả: {book.get('author')}",
                            f"- Giá: {book.get('price')} VND",
                            f"- Thể loại: {book.get('category_name') or 'Chưa phân loại'}",
                            f"- Tồn kho: {book.get('stock')}",
                            f"- Điểm đánh giá: {reviews.get('avg_rating', 0)}/5 ({reviews.get('total_reviews', 0)} lượt)",
                        ]
                        description = (book.get("description") or "").strip()
                        if description:
                            lines.append(f"- Mô tả: {description[:300]}")
                        lines.append("Bạn có thể nhắn: 'thêm sách id <ID> vào giỏ' nếu muốn mua ngay.")
                        return "\n".join(lines)
                    except Exception:
                        return "Mình chưa thể lấy chi tiết sách lúc này, bạn thử lại sau nhé."

        # Intent: thêm vào giỏ theo book_id
        if ("thêm" in lowered and "giỏ" in lowered) or ("add" in lowered and "cart" in lowered):
            import re
            match = re.search(r"(?:id\s*)?(\d+)", lowered)
            if match and user_id is not None:
                book_id = int(match.group(1))
                tool_fn = TOOL_FUNCTION_MAP.get("add_book_to_cart")
                if tool_fn:
                    try:
                        result = tool_fn(user_id=int(user_id), book_id=book_id, quantity=1)
                        payload = json.loads(result)
                        if payload.get("success"):
                            return f"Đã thêm sách ID {book_id} vào giỏ hàng của bạn thành công."
                        return f"Không thể thêm vào giỏ hàng: {payload.get('message') or payload.get('error') or 'Lỗi không xác định.'}"
                    except Exception:
                        return "Mình chưa thể thêm vào giỏ lúc này, bạn thử lại sau nhé."
            return "Bạn hãy gửi rõ ID sách cần thêm vào giỏ, ví dụ: 'thêm sách id 12 vào giỏ'."

        # Intent mặc định: tìm sách
        tool_fn = TOOL_FUNCTION_MAP.get("search_books")
        if tool_fn:
            try:
                result = tool_fn(query=user_message, category="")
                payload = json.loads(result)
                if not payload.get("found"):
                    return payload.get("message") or "Mình chưa tìm thấy sách phù hợp."

                books = payload.get("books", [])[:5]
                if not books:
                    return "Mình chưa tìm thấy sách phù hợp."

                lines = ["Mình tìm được một số sách phù hợp:"]
                for book in books:
                    lines.append(
                        f"- ID {book.get('id')}: {book.get('title')} ({book.get('author')}) - {book.get('price')} VND"
                    )
                lines.append("Bạn có thể nhắn: 'thêm sách id <ID> vào giỏ' để mình hỗ trợ tiếp.")
                return "\n".join(lines)
            except Exception:
                return "Mình chưa xử lý được yêu cầu lúc này, bạn vui lòng thử lại sau."

        return "Mình tạm thời không khả dụng. Bạn vui lòng thử lại sau nhé."


class AgentHistoryView(APIView):
    """
    Lấy lịch sử hội thoại của một session (hữu ích cho debug / hiển thị UI).

    GET /api/agent/history/<session_id>/
    """

    def get(self, request: Request, session_id: str) -> Response:
        limit   = int(request.query_params.get("limit", 20))
        history = get_chat_history(session_id, limit=limit)
        return Response({"session_id": session_id, "messages": history})
