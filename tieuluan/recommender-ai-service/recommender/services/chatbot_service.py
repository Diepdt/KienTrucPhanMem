import re
import logging
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Từ điển ngữ cảnh tư vấn ───────────────────────────────────────────────
_GREETING_PATTERNS = re.compile(
    r"^(xin ch[àa]o|ch[àa]o|hello|hi|hey|alo|hola|xin chao|chao)\s*[.!]*$",
    re.IGNORECASE | re.UNICODE,
)
_CHEAP_PATTERN = re.compile(
    r"r[eẻ]\s*nh[aấ]t|gi[aá]\s*th[aấ]p\s*nh[aấ]t|r[eẻ]\s*nh[aấ]t|cheapest",
    re.IGNORECASE | re.UNICODE,
)
_PRICE_PATTERN = re.compile(
    r"(?:dưới|duoi|<|<=|trên|tren|>|>=|khoảng|khoan|từ|tu)?\s*(\d[\d.,]*)\s*(?:k|nghìn|nghin|ngàn|ngan|đ|đồng|dong|vnđ|vnd)?",
    re.IGNORECASE | re.UNICODE,
)
_STOP_WORDS = {
    "có", "co", "không", "khong", "và", "va", "cái", "cai", "này", "nay",
    "đó", "do", "nào", "nao", "gì", "gi", "bao", "nhiều", "nhieu",
    "thế", "the", "thì", "thi", "mà", "ma", "hay", "với", "voi",
    "cho", "để", "de", "được", "duoc", "các", "cac", "những", "nhung",
    "một", "mot", "hai", "ba", "tôi", "toi", "bạn", "ban", "mình", "minh",
    "ạ", "a", "nhé", "nhe", "ơi", "oi", "shop",
    "của", "cua", "tìm", "tim", "muốn", "muon", "mua", "xem",
    "liên", "lien", "quan", "hỏi", "hoi", "giá", "gia",
    "sản", "san", "phẩm", "pham", "hàng", "hang", "tiền", "tien",
    "đến", "den", "ở", "o", "về", "ve", "theo", "thấy", "thay",
    "còn", "con", "cho", "loại", "loai", "nào", "nao",
}


def _parse_price_limit(text: str) -> Optional[int]:
    """Trả về ngưỡng giá (đơn vị VNĐ) nếu câu hỏi có đề cập giá."""
    # Normalize text trước để xử lý cả có dấu lẫn không dấu
    norm = _normalize(text)
    under = re.search(
        r"(?:duoi|duới|<|<=|toi da|toi|max|khong qua|chua|di)\s*(\d[\d.,]*)\s*(?:k|nghin|ngan|d|dong|vnd)?",
        norm,
        re.IGNORECASE,
    )
    # Fallback: tìm số + đơn vị trong text gốc
    if not under:
        under = re.search(
            r"(?:dưới|<|<=|tối đa|max|không quá)\s*(\d[\d.,]*)\s*(?:k|nghìn|ngàn|đ|đồng|vnđ|vnd)?",
            text,
            re.IGNORECASE | re.UNICODE,
        )
    if under:
        raw = under.group(1).replace(",", "").replace(".", "")
        val = int(raw)
        # Nếu nhỏ hơn 100000 thì coi là đơn vị nghìn (k)
        return val * 1000 if val < 100_000 else val
    return None


def _extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[\w]+", text.lower())
    return [t for t in tokens if len(t) > 2 and t not in _STOP_WORDS]


def _fetch_products(params: Dict[str, Any]) -> List[Dict]:
    """Gọi product-service để tìm sản phẩm, trả về list dict."""
    base_url = getattr(settings, "PRODUCT_SERVICE_URL", "http://product-service:8004")
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{base_url}/api/products/?{qs}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            # API trả về list hoặc {"results": [...]}
            if isinstance(data, list):
                return data
            return data.get("results", data.get("products", []))
    except Exception as exc:
        logger.warning("fetch_products failed: %s | url=%s", exc, url)
        return []


_ALL_PRODUCTS_CACHE: List[Dict] = []
_CACHE_TS: float = 0.0
_CACHE_TTL: float = 60.0  # cache 60 giây


def _normalize(text: str) -> str:
    """Chuẩn hoá text: lowercase + bỏ dấu (NFD → bỏ combining chars)."""
    import unicodedata
    # NFD decompose: 'ạ' → 'a' + combining dot below
    nfd = unicodedata.normalize("NFD", text.lower())
    # Giữ lại chỉ ASCII (bỏ tất cả combining diacritics)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def _get_all_products() -> List[Dict]:
    """Lấy tất cả sản phẩm active, cache 60s."""
    import time
    global _ALL_PRODUCTS_CACHE, _CACHE_TS
    now = time.time()
    if _ALL_PRODUCTS_CACHE and (now - _CACHE_TS) < _CACHE_TTL:
        return _ALL_PRODUCTS_CACHE
    products = _fetch_products({"is_active": "true"})
    if products:
        _ALL_PRODUCTS_CACHE = products
        _CACHE_TS = now
    return _ALL_PRODUCTS_CACHE


def _search_products(keywords: List[str], price_limit: Optional[int] = None, top_k: int = 6) -> List[Dict]:
    """Tìm sản phẩm: search API trước, nếu không ra thì search local (hỗ trợ không dấu)."""
    found: Dict[int, Dict] = {}

    base_params: Dict[str, Any] = {"is_active": "true"}
    if price_limit:
        base_params["max_price"] = str(price_limit)

    # Bước 1: thử search qua API (nhanh, có dấu)
    for kw in keywords[:4]:
        for p in _fetch_products({**base_params, "search": kw}):
            pid = p.get("id")
            if pid and pid not in found:
                found[pid] = p

    # Bước 2: nếu không ra, search toàn bộ sản phẩm và khớp không dấu
    if not found:
        all_products = _get_all_products()
        norm_keywords = [_normalize(kw) for kw in keywords]
        for p in all_products:
            # Lọc giá phía client nếu cần
            if price_limit and (_to_price(p) or float("inf")) > price_limit:
                continue
            # Xây chuỗi tìm kiếm từ name + category + product_type
            cat_name = ""
            if isinstance(p.get("category"), dict):
                cat_name = p["category"].get("name", "")
            elif p.get("category_name"):
                cat_name = p["category_name"]
            haystack = _normalize(
                f"{p.get('name', '')} {cat_name} {p.get('product_type', '')} {p.get('description', '')}"
            )
            if any(kw in haystack for kw in norm_keywords):
                pid = p.get("id")
                if pid and pid not in found:
                    found[pid] = p

    results = sorted(found.values(), key=lambda p: _to_price(p) or 0)
    return results[:top_k]


def _fetch_cheapest(top_k: int = 5) -> List[Dict]:
    """Lấy sản phẩm giá thấp nhất."""
    # Không hỗ trợ ordering qua API → lấy tất cả và sort phía client
    products = _fetch_products({"is_active": "true"})
    return sorted(products, key=lambda p: _to_price(p) or 0)[:top_k]


def _to_price(p: Dict) -> Optional[float]:
    try:
        return float(p.get("price", 0))
    except Exception:
        return None


def _fmt_price(price) -> str:
    try:
        v = int(float(price))
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}tr đ".replace(".0", "")
        return f"{v:,}đ".replace(",", ".")
    except Exception:
        return str(price)


def _product_line(p: Dict) -> str:
    name = p.get("name", "Sản phẩm")
    price = _fmt_price(p.get("price", 0))
    pid = p.get("id", "")
    ptype = p.get("product_type", "")
    cat = ""
    if isinstance(p.get("category"), dict):
        cat = p["category"].get("name", "")
    elif p.get("category_name"):
        cat = p["category_name"]
    label = f" [{cat}]" if cat else f" [{ptype}]" if ptype else ""
    return f"• {name}{label} — {price}  (ID: {pid})"


class ChatbotService:
    """Tư vấn bán hàng: tìm sản phẩm từ product-service, trả lời tiếng Việt."""

    def chat(self, user_id: int, message: str, top_k: int = 6) -> Dict[str, Any]:
        text = message.strip()

        # ── Chào hỏi ──────────────────────────────────────────────────────────
        if _GREETING_PATTERNS.match(text):
            return {
                "reply": (
                    "Xin chào! 👋 Mình là trợ lý tư vấn của cửa hàng.\n"
                    "Bạn có thể hỏi mình:\n"
                    "  • Tìm sản phẩm theo tên, danh mục\n"
                    "  • Sản phẩm dưới/trên mức giá nào đó\n"
                    "  • Sản phẩm rẻ nhất / mới nhất\n\n"
                    "Ví dụ: \"Tìm sách tâm linh\", \"Sản phẩm dưới 200k\", \"Laptop rẻ nhất\""
                ),
                "recommended_products": [],
            }

        # ── Sản phẩm rẻ nhất ─────────────────────────────────────────────────
        if _CHEAP_PATTERN.search(text):
            products = _fetch_cheapest(top_k)
            if products:
                lines = "\n".join(_product_line(p) for p in products)
                return {
                    "reply": f"Các sản phẩm giá rẻ nhất hiện tại:\n{lines}",
                    "recommended_products": products,
                }
            return {"reply": "Hiện tại chưa có dữ liệu sản phẩm.", "recommended_products": []}

        # ── Lọc theo giá ──────────────────────────────────────────────────────
        price_limit = _parse_price_limit(text)

        # ── Trích keywords ────────────────────────────────────────────────────
        keywords = _extract_keywords(text)

        # ── Tìm sản phẩm ─────────────────────────────────────────────────────
        products = _search_products(keywords, price_limit=price_limit, top_k=top_k)

        # ── Tạo câu trả lời ───────────────────────────────────────────────────
        if not products:
            kw_str = ", ".join(f'"{k}"' for k in keywords[:3]) if keywords else "từ khoá phù hợp"
            if price_limit:
                return {
                    "reply": (
                        f"Mình chưa tìm thấy sản phẩm nào dưới {_fmt_price(price_limit)} "
                        f"khớp với {kw_str}. 😅\n"
                        "Thử thay đổi từ khoá hoặc mức giá nhé!"
                    ),
                    "recommended_products": [],
                }
            return {
                "reply": (
                    f"Mình chưa tìm thấy sản phẩm nào khớp với {kw_str}. 😅\n"
                    "Thử tìm với từ khoá khác như: \"sách\", \"áo\", \"laptop\", \"điện thoại\"."
                ),
                "recommended_products": [],
            }

        lines = "\n".join(_product_line(p) for p in products)
        kw_display = " ".join(keywords[:4]) if keywords else text[:30]

        prefix = ""
        if price_limit:
            prefix = f"(dưới {_fmt_price(price_limit)}) "

        reply = (
            f"Mình tìm thấy {len(products)} sản phẩm {prefix}liên quan đến \"{kw_display}\":\n\n"
            f"{lines}\n\n"
            "Bạn muốn biết thêm chi tiết sản phẩm nào không?"
        )

        return {"reply": reply, "recommended_products": products}
