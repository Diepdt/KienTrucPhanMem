import os
from typing import Any, Dict, List

import requests

from .constants import DEFAULT_SERVICE_TYPES, PRODUCT_ENDPOINT_CANDIDATES


TIMEOUT = 8

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")

SERVICE_URLS = {
    "book": PRODUCT_SERVICE_URL,
    "laptop": PRODUCT_SERVICE_URL,
    "mobile": PRODUCT_SERVICE_URL,
    "cloth": PRODUCT_SERVICE_URL,
}


def _normalize_product(service_type: str, row: Dict[str, Any]) -> Dict[str, Any]:
    product_id = row.get("id") or row.get("product_id")
    return {
        "service_type": service_type,
        "product_id": int(product_id) if product_id is not None else 0,
        "name": row.get("name") or row.get("title") or f"{service_type}-{product_id}",
        "description": row.get("description") or "",
        "price": row.get("price") or 0,
        "category": row.get("category") or service_type,
        "raw": row,
    }


def fetch_products_for_service(service_type: str) -> List[Dict[str, Any]]:
    base_url = SERVICE_URLS.get(service_type)
    if not base_url:
        return []

    endpoints = PRODUCT_ENDPOINT_CANDIDATES.get(service_type, ["/api/"])
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            items = payload.get("results", payload) if isinstance(payload, dict) else payload
            if not isinstance(items, list):
                continue
            return [_normalize_product(service_type, item) for item in items if isinstance(item, dict)]
        except Exception:
            continue

    return []


def fetch_all_products() -> List[Dict[str, Any]]:
    products: List[Dict[str, Any]] = []
    for service_type in DEFAULT_SERVICE_TYPES:
        products.extend(fetch_products_for_service(service_type))
    return products
