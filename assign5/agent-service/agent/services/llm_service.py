"""
agent/services/llm_service.py
────────────────────────────────────────────────────────────────
Tầng gọi Gemini API (Google AI Studio) qua OpenAI-compatible endpoint.
Gemini hỗ trợ cùng định dạng request/response với OpenAI Chat Completions,
nên không cần cài thêm thư viện – chỉ đổi base URL và API key.

Docs: https://ai.google.dev/gemini-api/docs/openai

Public API:
  • call_llm()             – Gửi request tới Gemini, trả về dict.
  • extract_tool_calls()   – Trích xuất danh sách tool_calls từ response.
  • extract_text_content() – Trích xuất nội dung văn bản từ response.
"""

import logging
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Gemini OpenAI-compatible endpoint
_GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def call_llm(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: str = "auto",
) -> Dict[str, Any]:
    """
    Gửi danh sách messages đến Gemini API (OpenAI-compatible endpoint).

    Args:
        messages:    Mảng message theo chuẩn OpenAI [{role, content}, ...].
        tools:       Danh sách tool definitions JSON (None = không dùng tools).
        tool_choice: Chiến lược chọn tool ("auto", "none", hoặc tên tool cụ thể).

    Returns:
        Dict chứa response JSON đầy đủ (cùng định dạng OpenAI).

    Raises:
        requests.HTTPError: Khi API trả về HTTP error (4xx/5xx).
        requests.Timeout:   Khi request vượt quá thời gian chờ.
        RuntimeError:       Khi GEMINI_API_KEY chưa được cấu hình.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY chưa được cấu hình. "
            "Lấy key miễn phí tại https://aistudio.google.com/app/apikey"
        )

    model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    logger.debug("call_llm → model=%s, msg_count=%d, has_tools=%s", model, len(messages), bool(tools))

    response = requests.post(
        _GEMINI_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if not response.ok:
        try:
            err_body = response.json()
            err_code = err_body.get("error", {}).get("code", "")
            err_msg  = err_body.get("error", {}).get("message", "")
            logger.error("Gemini API error %s – code=%s msg=%s", response.status_code, err_code, err_msg)
            if response.status_code == 429:
                raise RuntimeError(
                    "Gemini API đang bị rate limit. Vui lòng thử lại sau vài giây."
                )
            if response.status_code in (401, 403):
                raise RuntimeError(
                    "GEMINI_API_KEY không hợp lệ hoặc không có quyền. "
                    "Kiểm tra lại key tại https://aistudio.google.com/app/apikey"
                )
        except RuntimeError:
            raise
        except Exception:
            pass
        response.raise_for_status()

    data = response.json()
    logger.debug(
        "call_llm ← finish_reason=%s, usage=%s",
        data.get("choices", [{}])[0].get("finish_reason"),
        data.get("usage"),
    )
    return data


def extract_tool_calls(llm_response: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Trích xuất danh sách tool_calls từ response của LLM.

    Args:
        llm_response: Dict JSON trả về từ call_llm().

    Returns:
        Danh sách tool_call objects nếu LLM yêu cầu gọi tool,
        None nếu LLM trả lời văn bản trực tiếp.
    """
    try:
        choice       = llm_response["choices"][0]
        finish_reason = choice.get("finish_reason", "")
        tool_calls   = choice["message"].get("tool_calls")

        if finish_reason == "tool_calls" and tool_calls:
            return tool_calls
    except (KeyError, IndexError) as exc:
        logger.error("extract_tool_calls parse error: %s", exc)
    return None


def extract_text_content(llm_response: Dict[str, Any]) -> str:
    """
    Trích xuất nội dung văn bản (content) từ response LLM.

    Args:
        llm_response: Dict JSON trả về từ call_llm().

    Returns:
        Chuỗi nội dung hoặc chuỗi rỗng nếu không có.
    """
    try:
        return llm_response["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError):
        return ""
