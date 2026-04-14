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
    "book": ["/api/books/", "/api/book/"],
    "laptop": ["/api/laptops/", "/api/laptop/"],
    "mobile": ["/api/mobiles/", "/api/mobile/"],
    "cloth": ["/api/clothes/", "/api/cloth/"],
}
