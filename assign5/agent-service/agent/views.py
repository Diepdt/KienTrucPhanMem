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
            # Lỗi cấu hình (thiếu API key, v.v.)
            logger.error("AgentChatView config error: %s", exc)
            return Response(
                {"error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.error("AgentChatView unexpected error: %s", exc, exc_info=True)
            exc_str = str(exc)
            if "429" in exc_str:
                user_msg = (
                    "BookBot hiện đang quá tải hoặc API key đã hết hạn. "
                    "Vui lòng thử lại sau ít phút."
                )
            elif "401" in exc_str or "Unauthorized" in exc_str:
                user_msg = "API key OpenAI không hợp lệ. Vui lòng kiểm tra cấu hình."
            elif "Connection" in exc_str or "Timeout" in exc_str:
                user_msg = "Không kết nối được tới dịch vụ AI. Vui lòng thử lại sau."
            else:
                user_msg = "Xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
            return Response(
                {"error": user_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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


class AgentHistoryView(APIView):
    """
    Lấy lịch sử hội thoại của một session (hữu ích cho debug / hiển thị UI).

    GET /api/agent/history/<session_id>/
    """

    def get(self, request: Request, session_id: str) -> Response:
        limit   = int(request.query_params.get("limit", 20))
        history = get_chat_history(session_id, limit=limit)
        return Response({"session_id": session_id, "messages": history})
