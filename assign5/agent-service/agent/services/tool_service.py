"""
agent/services/tool_service.py
────────────────────────────────────────────────────────────────
Module 1 – Tool Functions (Công cụ nội bộ cho Agent)

Gồm:
  • TOOL_DEFINITIONS  – JSON Schema theo chuẩn OpenAI function-calling.
  • search_books()    – Wrapper gọi book-service để tìm kiếm sách.
  • add_book_to_cart()– Wrapper gọi cart-service để thêm sách vào giỏ.
  • TOOL_FUNCTION_MAP – Ánh xạ tên hàm → callable để Execution Loop dùng.
"""

import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# JSON Schema Definitions (chuẩn OpenAI tools array)
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": (
                "Tìm kiếm sách trong hệ thống theo từ khóa (tên sách hoặc tên tác giả) "
                "và/hoặc danh mục. Gọi hàm này khi khách hàng muốn tìm sách, hỏi về "
                "sách cụ thể, hỏi về tác giả, hoặc yêu cầu gợi ý sách theo thể loại."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Từ khóa tìm kiếm: tên sách hoặc tên tác giả. "
                            "Ví dụ: 'Dắt tôi qua bóng tối' hoặc 'Nguyễn Nhật Ánh'. "
                            "Truyền chuỗi rỗng nếu chỉ lọc theo danh mục."
                        ),
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "Tên danh mục sách để lọc kết quả. "
                            "Ví dụ: 'Văn học', 'Khoa học', 'Thiếu nhi', 'Kinh tế'. "
                            "Truyền chuỗi rỗng nếu không cần lọc theo danh mục."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_book_to_cart",
            "description": (
                "Thêm một cuốn sách vào giỏ hàng của khách hàng đang đăng nhập. "
                "CHỈ gọi hàm này khi khách hàng xác nhận rõ ràng muốn mua hoặc thêm "
                "một cuốn sách CỤ THỂ (đã có book_id từ kết quả search_books) vào giỏ. "
                "Không được tự suy đoán book_id; hãy tìm sách trước rồi mới gọi hàm này."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID của khách hàng đang đăng nhập (lấy từ context cuộc hội thoại).",
                    },
                    "book_id": {
                        "type": "integer",
                        "description": "ID của cuốn sách cần thêm, lấy từ kết quả search_books.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Số lượng muốn thêm vào giỏ. Mặc định là 1 nếu khách không chỉ định.",
                        "default": 1,
                    },
                },
                "required": ["user_id", "book_id", "quantity"],
            },
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Tool Implementations
# ─────────────────────────────────────────────────────────────────────────────

def search_books(query: str, category: str = "") -> str:
    """
    Tìm kiếm sách từ book-service theo từ khóa (title / author) và danh mục.

    Args:
        query:    Từ khóa tên sách hoặc tên tác giả.
        category: Danh mục sách để lọc (tùy chọn).

    Returns:
        Chuỗi JSON chứa danh sách sách tìm được hoặc thông báo lỗi.
    """
    try:
        base_url = f"{settings.BOOK_SERVICE_URL}/api/books/"
        seen_ids: set = set()
        results: list = []

        # Tìm theo title
        if query:
            resp = requests.get(base_url, params={"title": query}, timeout=10)
            resp.raise_for_status()
            for book in resp.json():
                if book["id"] not in seen_ids:
                    results.append(book)
                    seen_ids.add(book["id"])

        # Tìm theo author (loại trùng theo id)
        if query:
            resp = requests.get(base_url, params={"author": query}, timeout=10)
            resp.raise_for_status()
            for book in resp.json():
                if book["id"] not in seen_ids:
                    results.append(book)
                    seen_ids.add(book["id"])

        # Nếu không có query, lấy toàn bộ để lọc theo category
        if not query:
            resp = requests.get(base_url, timeout=10)
            resp.raise_for_status()
            for book in resp.json():
                results.append(book)

        # Lọc theo category (client-side) nếu được chỉ định
        if category and results:
            results = [
                b for b in results
                if category.lower() in (b.get("category_name") or "").lower()
            ]

        if not results:
            return json.dumps(
                {"found": False, "message": "Không tìm thấy sách nào phù hợp với yêu cầu."},
                ensure_ascii=False,
            )

        # Giữ tối đa 10 kết quả, chỉ các trường cần thiết để tiết kiệm token
        simplified = [
            {
                "id": b["id"],
                "title": b["title"],
                "author": b["author"],
                "price": str(b["price"]),
                "stock": b["stock"],
                "category_name": b.get("category_name", ""),
                "description": (b.get("description") or "")[:200],
                "cover_url": b.get("cover_url", ""),
            }
            for b in results[:10]
        ]
        return json.dumps(
            {"found": True, "count": len(simplified), "books": simplified},
            ensure_ascii=False,
        )

    except requests.exceptions.ConnectionError:
        logger.error("search_books: không kết nối được book-service")
        return json.dumps({"error": "Dịch vụ sách hiện không khả dụng, vui lòng thử lại sau."}, ensure_ascii=False)
    except requests.exceptions.Timeout:
        logger.error("search_books: book-service timeout")
        return json.dumps({"error": "Yêu cầu tìm sách quá thời gian chờ, vui lòng thử lại."}, ensure_ascii=False)
    except Exception as exc:
        logger.error("search_books unexpected error: %s", exc, exc_info=True)
        return json.dumps({"error": f"Lỗi không xác định khi tìm sách: {exc}"}, ensure_ascii=False)


def add_book_to_cart(user_id: int, book_id: int, quantity: int = 1) -> str:
    """
    Thêm sách vào giỏ hàng thông qua cart-service (internal endpoint).

    Args:
        user_id:  ID khách hàng (customer_id).
        book_id:  ID cuốn sách cần thêm.
        quantity: Số lượng (mặc định 1).

    Returns:
        Chuỗi JSON chứa trạng thái thao tác và thông tin giỏ hàng.
    """
    try:
        resp = requests.post(
            f"{settings.CART_SERVICE_URL}/api/carts/add-internal/",
            json={"customer_id": user_id, "book_id": book_id, "quantity": quantity},
            timeout=10,
        )

        if resp.status_code in (200, 201):
            return json.dumps(
                {
                    "success": True,
                    "message": f"Đã thêm {quantity} cuốn (book_id={book_id}) vào giỏ hàng thành công!",
                    "cart": resp.json(),
                },
                ensure_ascii=False,
            )

        # Lỗi nghiệp vụ từ cart-service (400, 404, …)
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        return json.dumps(
            {"success": False, "message": "Thêm vào giỏ hàng thất bại.", "detail": detail},
            ensure_ascii=False,
        )

    except requests.exceptions.ConnectionError:
        logger.error("add_book_to_cart: không kết nối được cart-service")
        return json.dumps({"success": False, "error": "Dịch vụ giỏ hàng hiện không khả dụng."}, ensure_ascii=False)
    except requests.exceptions.Timeout:
        logger.error("add_book_to_cart: cart-service timeout")
        return json.dumps({"success": False, "error": "Yêu cầu giỏ hàng quá thời gian chờ."}, ensure_ascii=False)
    except Exception as exc:
        logger.error("add_book_to_cart unexpected error: %s", exc, exc_info=True)
        return json.dumps({"success": False, "error": f"Lỗi không xác định: {exc}"}, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch map – Execution Loop dùng để map tên hàm → callable
# ─────────────────────────────────────────────────────────────────────────────

TOOL_FUNCTION_MAP: dict = {
    "search_books": search_books,
    "add_book_to_cart": add_book_to_cart,
}
