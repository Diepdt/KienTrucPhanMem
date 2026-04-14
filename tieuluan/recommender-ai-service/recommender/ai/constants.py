EVENT_WEIGHTS = {
    "view": 1.0,
    "click": 1.2,
    "add_to_cart": 2.5,
    "purchase": 4.0,
    "search": 0.8,
    "chat": 0.5,
}

DEFAULT_SERVICE_TYPES = ["book", "laptop", "mobile", "cloth"]

PRODUCT_ENDPOINT_CANDIDATES = {
    "book": ["/api/products/?product_type=book"],
    "laptop": ["/api/products/?product_type=laptop"],
    "mobile": ["/api/products/?product_type=mobile"],
    "cloth": ["/api/products/?product_type=cloth"],
}
