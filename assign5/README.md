# BookStore Microservices

Hệ thống BookStore phân rã thành Microservices sử dụng Django REST Framework, Docker Compose, và MySQL độc lập cho từng service.

---

## 1. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               API GATEWAY  :8000  (SQLite)                       │
│         Proxy / Route tất cả request vào service phù hợp        │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────┘
   │      │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
:8001  :8002  :8003  :8004  :8005  :8006  :8007  :8008  :8009  :8010  :8011
staff  mgr   cust  catalog  book   cart  order  ship   pay   comment recomm
```

### Sơ đồ giao tiếp giữa các service (Inter-service calls)

```
customer-service ──────────────────────────────► cart-service
  (POST /register)                               (POST /carts/create/)

book-service ──────────────────────────────────► staff-service
  (verify staff token)                           (GET /staff/verify-token/)

book-service ──────────────────────────────────► catalog-service
  (get category name)                            (GET /categories/{id}/)

cart-service ──────────────────────────────────► customer-service
  (verify customer token)                        (GET /customers/verify-token/)

cart-service ──────────────────────────────────► book-service
  (check stock)                                  (GET /books/{id}/)

order-service ─────────────────────────────────► customer-service
  (verify token)                                 (GET /customers/verify-token/)

order-service ─────────────────────────────────► cart-service
  (get cart, clear cart)                         (GET /carts/{id}/internal/
                                                  POST /carts/{id}/clear/)

order-service ─────────────────────────────────► ship-service
  (get method, create shipment)                  (GET /shipping/methods/{id}/
                                                  POST /shipping/create/)

order-service ─────────────────────────────────► pay-service
  (get method, create payment)                   (GET /payment/methods/{id}/
                                                  POST /payment/create/)

order-service ─────────────────────────────────► book-service
  (update stock)                                 (POST /books/update-stock/)

comment-service ───────────────────────────────► customer-service
  (verify token)                                 (GET /customers/verify-token/)

recommender-service ───────────────────────────► comment-service
  (all reviews)                                  (GET /reviews/all-internal/)

recommender-service ───────────────────────────► order-service
  (customer orders)                              (GET /orders/customer/{id}/internal/)

recommender-service ───────────────────────────► book-service
  (all books)                                    (GET /books/)

manager-service ───────────────────────────────► staff-service
  (manage staff)                                 (GET|POST /staffs/)
```

---

## 2. Bảng các Service

| Service | Port | Database | Chức năng |
|---------|------|----------|-----------|
| api-gateway | 8000 | SQLite | Proxy/định tuyến tất cả request |
| staff-service | 8001 | db_staff | Quản lý nhân viên, xác thực staff token |
| manager-service | 8002 | db_manager | Quản lý quản lý, phân quyền quản lý staff |
| customer-service | 8003 | db_customer | Đăng ký/đăng nhập/xác thực khách hàng |
| catalog-service | 8004 | db_catalog | Danh mục sách phân cấp |
| book-service | 8005 | db_book | CRUD sách (staff), tìm kiếm, cập nhật tồn kho |
| cart-service | 8006 | db_cart | Giỏ hàng (tự tạo khi đăng ký) |
| order-service | 8007 | db_order | Đặt hàng, kích hoạt thanh toán + vận chuyển |
| ship-service | 8008 | db_ship | Phương thức & lô vận chuyển |
| pay-service | 8009 | db_pay | Phương thức & giao dịch thanh toán |
| comment-rate-service | 8010 | db_comment | Đánh giá & chấm điểm sách |
| recommender-ai-service | 8011 | db_recommender | Gợi ý sách AI (content-based + popularity) |

---

## 3. Khởi chạy

```bash
docker compose up --build
```

Kiểm tra trạng thái tất cả service:
```
GET http://localhost:8000/api/health/
```

---

## 4. API Documentation

> Tất cả request đều đi qua **API Gateway** tại `http://localhost:8000`
>
> Header xác thực: `Authorization: Token <token>`

---

### 4.1 Staff Service — `/api/staff*` và `/api/staffs*`

#### Đăng nhập nhân viên
```
POST /api/staff/login/
Body: { "email": "staff@example.com", "password": "123456" }
Response 200: { "token": "abc...", "staff": { "id", "name", "email", "role", ... } }
```

#### Đăng xuất nhân viên
```
POST /api/staff/logout/
Header: Authorization: Token <token>
Response 200: { "message": "Logged out" }
```

#### Xác thực staff token (internal)
```
GET /api/staff/verify-token/
Header: Authorization: Token <token>
Response 200: { "valid": true, "staff": { "id", "name", "email", "role" } }
Response 401: { "valid": false }
```

#### Danh sách nhân viên
```
GET /api/staffs/
Response 200: [ { "id", "name", "email", "phone", "role", "is_active", "created_at" } ]
```

#### Tạo nhân viên mới
```
POST /api/staffs/
Body: { "name": "Nguyen Van A", "email": "a@store.com", "password": "123", "phone": "09xx", "role": "staff" }
Response 201: { "id", "name", "email", "phone", "role", "is_active", "created_at" }
```

#### Cập nhật nhân viên
```
PUT /api/staffs/{id}/
Body: { "name": "...", "phone": "..." }
Response 200: { ...staff object... }
```

#### Vô hiệu hóa nhân viên (soft delete)
```
DELETE /api/staffs/{id}/
Response 200: { "message": "Staff deactivated" }
```

---

### 4.2 Manager Service — `/api/manager*` và `/api/managers*`

#### Đăng nhập quản lý
```
POST /api/manager/login/
Body: { "email": "mgr@example.com", "password": "123456" }
Response 200: { "token": "abc...", "manager": { "id", "name", "email", ... } }
```

#### Xác thực manager token (internal)
```
GET /api/manager/verify-token/
Header: Authorization: Token <token>
Response 200: { "valid": true, "manager": { ... } }
```

#### Danh sách quản lý
```
GET /api/managers/
Response 200: [ { "id", "name", "email", "phone", "is_active", "created_at" } ]
```

#### Tạo quản lý mới
```
POST /api/managers/
Body: { "name": "Le Thi B", "email": "b@store.com", "password": "123", "phone": "09xx" }
Response 201: { ...manager object... }
```

#### Quản lý danh sách nhân viên (qua staff-service)
```
GET  /api/manager/staff/
Header: Authorization: Token <manager_token>
Response 200: [ ...danh sách staff... ]

POST /api/manager/staff/
Header: Authorization: Token <manager_token>
Body: { "name": "...", "email": "...", "password": "...", "role": "staff" }
Response 201: { ...staff object... }
```

---

### 4.3 Customer Service — `/api/customers*`

#### Đăng ký khách hàng (tự động tạo giỏ hàng)
```
POST /api/customers/register/
Body: { "name": "Tran Van C", "email": "c@mail.com", "password": "123", "phone": "09xx", "address": "..." }
Response 201: {
  "message": "Đăng ký thành công. Giỏ hàng đã được tạo tự động.",
  "token": "abc...",
  "customer": { "id", "name", "email", "phone", "address", "is_active", "created_at" }
}
```

#### Đăng nhập
```
POST /api/customers/login/
Body: { "email": "c@mail.com", "password": "123" }
Response 200: { "token": "abc...", "customer": { ... } }
```

#### Đăng xuất
```
POST /api/customers/logout/
Header: Authorization: Token <token>
Response 200: { "message": "Đăng xuất thành công" }
```

#### Xem thông tin khách hàng
```
GET /api/customers/{customer_id}/
Response 200: { "id", "name", "email", "phone", "address", "is_active", "created_at" }
```

#### Cập nhật thông tin (chỉ chính mình)
```
PUT /api/customers/{customer_id}/
Header: Authorization: Token <token>
Body: { "name": "...", "phone": "...", "address": "..." }
Response 200: { ...customer object... }
```

#### Xác thực customer token (internal)
```
GET /api/customers/verify-token/
Header: Authorization: Token <token>
Response 200: { "valid": true, "customer": { ... } }
```

#### Danh sách tất cả khách hàng
```
GET /api/customers/
Response 200: [ { ...customer objects... } ]
```

---

### 4.4 Catalog Service — `/api/categories*`

#### Danh sách danh mục (kèm sub-categories)
```
GET /api/categories/
Response 200: [
  {
    "id": 1, "name": "Văn học", "description": "...", "parent": null,
    "subcategories": [
      { "id": 3, "name": "Tiểu thuyết", "parent": 1, "subcategories": [] }
    ],
    "created_at": "..."
  }
]
```

#### Chi tiết danh mục
```
GET /api/categories/{id}/
Response 200: { "id", "name", "description", "parent", "subcategories", "created_at" }
```

#### Tạo danh mục mới
```
POST /api/categories/
Body: { "name": "Khoa học", "description": "...", "parent": null }
       # parent: null = danh mục gốc, parent: <id> = sub-category
Response 201: { "id", "name", "description", "parent", "subcategories", "created_at" }
```

---

### 4.5 Book Service — `/api/books*`

#### Danh sách sách (có filter)
```
GET /api/books/
GET /api/books/?category_id=1
GET /api/books/?author=Nguyen
GET /api/books/?title=Harry
Response 200: [ { "id", "title", "author", "isbn", "price", "stock", "category_id",
                  "category_name", "description", "cover_url", "is_active",
                  "created_by_staff_id", "created_at" } ]
```

#### Chi tiết sách
```
GET /api/books/{id}/
Response 200: { ...book object... }
Response 404: { "error": "Sách không tồn tại" }
```

#### Thêm sách mới (Staff only)
```
POST /api/books/
Header: Authorization: Token <staff_token>
Body: {
  "title": "Lập trình Python",
  "author": "Nguyen Van A",
  "isbn": "978-x-xxx-xxxxx-x",
  "price": "120000.00",
  "stock": 50,
  "category_id": 2,
  "description": "...",
  "cover_url": "https://..."
}
Response 201: { ...book object với category_name được tự động lấy từ catalog-service... }
Response 403: { "error": "Chỉ nhân viên mới được thêm sách" }
```

#### Cập nhật sách (Staff only)
```
PUT /api/books/{id}/
Header: Authorization: Token <staff_token>
Body: { "price": "150000.00", "stock": 100 }   # partial update
Response 200: { ...book object... }
```

#### Xóa sách / soft delete (Staff only)
```
DELETE /api/books/{id}/
Header: Authorization: Token <staff_token>
Response 200: { "message": "Sách đã được xóa" }
```

#### Cập nhật tồn kho (internal — order-service gọi)
```
POST /api/books/update-stock/
Body: { "items": [ { "book_id": 1, "quantity": 2 }, { "book_id": 3, "quantity": 1 } ] }
Response 200: { "message": "Tồn kho đã được cập nhật" }
Response 400: { "errors": [ { "book_id": 1, "error": "Không đủ hàng" } ] }
```

---

### 4.6 Cart Service — `/api/carts*`

#### Xem giỏ hàng
```
GET /api/carts/{customer_id}/
Header: Authorization: Token <customer_token>
Response 200: {
  "id": 1, "customer_id": 5,
  "items": [
    { "id", "book_id", "book_title", "book_author", "price", "quantity", "item_total" }
  ],
  "total": "250000.00",
  "created_at": "...", "updated_at": "..."
}
```

#### Thêm sách vào giỏ
```
POST /api/carts/add/
Header: Authorization: Token <customer_token>
Body: { "book_id": 3, "quantity": 2 }
Response 200: { ...cart object với items đã cập nhật... }
Response 400: { "error": "Sách không đủ số lượng trong kho" }
Response 404: { "error": "Sách không tồn tại" }
```

#### Cập nhật số lượng item
```
PUT /api/carts/items/{item_id}/
Header: Authorization: Token <customer_token>
Body: { "quantity": 3 }
Response 200: { ...cart item object... }
# Nếu quantity <= 0 → item bị xóa tự động
Response 200: { "message": "Đã xóa sản phẩm khỏi giỏ hàng" }
```

#### Xóa item khỏi giỏ
```
DELETE /api/carts/items/{item_id}/remove/
Header: Authorization: Token <customer_token>
Response 200: { "message": "Đã xóa sản phẩm khỏi giỏ hàng" }
```

#### Tạo giỏ hàng (internal — customer-service gọi)
```
POST /api/carts/create/
Body: { "customer_id": 5 }
Response 201: { ...cart object... }
```

#### Xóa toàn bộ giỏ hàng (internal — order-service gọi)
```
POST /api/carts/{customer_id}/clear/
Response 200: { "message": "Giỏ hàng đã được xóa sạch" }
```

---

### 4.7 Order Service — `/api/orders*`

#### Đặt hàng
```
POST /api/orders/create/
Header: Authorization: Token <customer_token>
Body: {
  "shipping_method_id": 1,
  "payment_method_id": 2,
  "shipping_address": "123 Nguyen Trai, Q1, TP.HCM",
  "notes": "Giao giờ hành chính"
}
Response 201: {
  "order": {
    "id", "customer_id",
    "shipping_method_id", "shipping_method_name", "shipping_cost",
    "payment_method_id", "payment_method_name",
    "subtotal", "total_amount", "status",
    "shipping_address", "notes",
    "items": [ { "book_id", "book_title", "price", "quantity", "item_total" } ],
    "created_at", "updated_at"
  },
  "payment": { "id", "order_id", "method_name", "amount", "status", "transaction_id" },
  "shipment": { "id", "order_id", "method_name", "status", "tracking_number", "estimated_delivery" }
}
Response 400: { "error": "Giỏ hàng trống, không thể đặt hàng" }
```

#### Danh sách đơn hàng của khách hàng
```
GET /api/orders/
Header: Authorization: Token <customer_token>
Response 200: [ { ...order objects... } ]
```

#### Chi tiết đơn hàng
```
GET /api/orders/{order_id}/
Header: Authorization: Token <customer_token>
Response 200: { ...order object với items... }
```

#### Hủy đơn hàng (chỉ khi pending/confirmed)
```
PATCH /api/orders/{order_id}/
Header: Authorization: Token <customer_token>
Body: {}   # không cần body
Response 200: { ...order object với status: "cancelled"... }
Response 400: { "error": "Không thể hủy đơn hàng ở trạng thái này" }
```

---

### 4.8 Ship Service — `/api/shipping*`

#### Danh sách phương thức vận chuyển
```
GET /api/shipping/methods/
Response 200: [
  { "id": 1, "name": "Giao hàng tiêu chuẩn", "description": "...", "cost": "30000.00", "delivery_days": 3, "is_active": true },
  { "id": 2, "name": "Giao hàng nhanh", "description": "...", "cost": "50000.00", "delivery_days": 1, "is_active": true }
]
```

#### Tạo phương thức vận chuyển mới
```
POST /api/shipping/methods/
Body: { "name": "Giao hàng hỏa tốc", "cost": "80000.00", "delivery_days": 0 }
Response 201: { ...shipping method object... }
```

#### Chi tiết phương thức vận chuyển
```
GET /api/shipping/methods/{id}/
Response 200: { "id", "name", "description", "cost", "delivery_days", "is_active" }
```

#### Trạng thái vận chuyển theo đơn hàng
```
GET /api/shipping/order/{order_id}/
Response 200: {
  "id", "order_id", "method", "method_name",
  "status": "pending|processing|shipped|delivered|failed|returned",
  "shipping_address", "tracking_number", "estimated_delivery",
  "created_at", "updated_at"
}
```

#### Cập nhật trạng thái vận chuyển
```
PATCH /api/shipping/order/{order_id}/
Body: { "status": "shipped" }
Response 200: { ...shipment object... }
```

---

### 4.9 Pay Service — `/api/payment*`

#### Danh sách phương thức thanh toán
```
GET /api/payment/methods/
Response 200: [
  { "id": 1, "name": "Tiền mặt khi nhận hàng (COD)", "description": "...", "is_active": true },
  { "id": 2, "name": "Chuyển khoản ngân hàng", "description": "...", "is_active": true }
]
```

#### Tạo phương thức thanh toán mới
```
POST /api/payment/methods/
Body: { "name": "Ví điện tử MoMo", "description": "..." }
Response 201: { ...payment method object... }
```

#### Chi tiết phương thức thanh toán
```
GET /api/payment/methods/{id}/
Response 200: { "id", "name", "description", "is_active" }
```

#### Trạng thái thanh toán theo đơn hàng
```
GET /api/payment/order/{order_id}/
Response 200: {
  "id", "order_id", "method", "method_name", "amount",
  "status": "pending|processing|completed|failed|refunded",
  "transaction_id", "notes", "created_at", "updated_at"
}
```

#### Cập nhật trạng thái thanh toán
```
PATCH /api/payment/order/{order_id}/
Body: { "status": "completed" }
Response 200: { ...payment object... }
```

---

### 4.10 Comment & Rate Service — `/api/reviews*`

#### Đánh giá sách (tạo mới hoặc cập nhật)
```
POST /api/reviews/
Header: Authorization: Token <customer_token>
Body: { "book_id": 3, "rating": 5, "comment": "Sách rất hay!" }
Response 201: { "message": "Đánh giá đã được tạo.", "review": { ... } }
Response 200: { "message": "Đánh giá đã được cập nhật.", "review": { ... } }
# rating: 1–5 (bắt buộc)
```

#### Tất cả đánh giá của một cuốn sách
```
GET /api/reviews/books/{book_id}/
Response 200: {
  "book_id": 3,
  "avg_rating": 4.25,
  "total_reviews": 8,
  "reviews": [ { "id", "customer_id", "book_id", "rating", "comment", "created_at" } ]
}
```

#### Đánh giá của chính mình
```
GET /api/reviews/mine/
Header: Authorization: Token <customer_token>
Response 200: [ { "id", "customer_id", "book_id", "rating", "comment", "created_at" } ]
```

#### Điểm trung bình nhiều sách (internal)
```
GET /api/reviews/avg-ratings/?book_ids=1,2,3,5
Response 200: {
  "1": { "avg_rating": 4.5, "count": 12 },
  "2": { "avg_rating": 3.8, "count": 5 },
  ...
}
```

---

### 4.11 Recommender AI Service — `/api/recommendations*`

#### Tính toán và lấy gợi ý sách (tính mới + cache)
```
GET /api/recommendations/{customer_id}/
Response 200: {
  "customer_id": 5,
  "total": 8,
  "recommendations": [
    {
      "book_id": 12,
      "score": 4.85,
      "avg_rating": 4.7,
      "review_count": 20,
      "reason": "Đánh giá trung bình 4.7★ từ 20 người dùng"
    },
    ...
  ]
}
```

#### Lấy gợi ý từ cache (nhanh hơn)
```
GET /api/recommendations/{customer_id}/cached/
Response 200: {
  "customer_id": 5,
  "total": 8,
  "recommendations": [ { "book_id", "score", "reason" } ]
}
# Nếu chưa có cache → tự động tính lại
```

**Thuật toán gợi ý:**
- Thu thập tất cả đánh giá từ comment-service
- Lấy lịch sử mua của khách từ order-service
- Loại trừ sách đã mua / đã đánh giá
- `Score = avg_rating × 0.7 + popularity × 0.3 × 5`
- Chỉ gợi ý sách có `avg_rating ≥ 3.5`
- Trả về top 10

---

### 4.12 API Gateway — Health Check

```
GET /api/health/
Response 200: {
  "gateway": "up",
  "services": {
    "staff-service":           { "status": "up",   "url": "http://staff-service:8001" },
    "manager-service":         { "status": "up",   "url": "http://manager-service:8002" },
    "customer-service":        { "status": "up",   "url": "http://customer-service:8003" },
    "catalog-service":         { "status": "up",   "url": "http://catalog-service:8004" },
    "book-service":            { "status": "up",   "url": "http://book-service:8005" },
    "cart-service":            { "status": "up",   "url": "http://cart-service:8006" },
    "order-service":           { "status": "up",   "url": "http://order-service:8007" },
    "ship-service":            { "status": "up",   "url": "http://ship-service:8008" },
    "pay-service":             { "status": "up",   "url": "http://pay-service:8009" },
    "comment-rate-service":    { "status": "up",   "url": "http://comment-rate-service:8010" },
    "recommender-ai-service":  { "status": "up",   "url": "http://recommender-ai-service:8011" }
  },
  "overall": "healthy"
}
```

---

## 5. Luồng nghiệp vụ chính

### Luồng 1 — Đăng ký → Giỏ hàng tự động
```
Client → POST /api/customers/register/
         └─ customer-service tạo Customer
         └─ customer-service gọi POST /api/carts/create/ → cart-service tạo Cart
         └─ Trả về token + customer info
```

### Luồng 2 — Staff thêm sách
```
Staff → POST /api/staff/login/ → nhận Token
Staff → POST /api/books/  (Authorization: Token <staff_token>)
        └─ book-service gọi GET /api/staff/verify-token/ → staff-service xác thực
        └─ book-service gọi GET /api/categories/{id}/ → catalog-service lấy tên danh mục
        └─ Tạo Book với category_name snapshot
```

### Luồng 3 — Thêm vào giỏ hàng
```
Customer → POST /api/carts/add/  { book_id, quantity }
           └─ cart-service gọi GET /api/customers/verify-token/ → xác thực
           └─ cart-service gọi GET /api/books/{id}/ → kiểm tra tồn kho
           └─ Thêm/cộng dồn CartItem
```

### Luồng 4 — Đặt hàng (luồng phức tạp nhất)
```
Customer → POST /api/orders/create/  { shipping_method_id, payment_method_id, shipping_address }
           └─ 1. order-service xác thực token qua customer-service
           └─ 2. Lấy giỏ hàng từ cart-service (internal endpoint)
           └─ 3. Lấy thông tin ship method từ ship-service
           └─ 4. Lấy thông tin pay method từ pay-service
           └─ 5. Tính subtotal + shipping_cost = total
           └─ 6. Tạo Order + OrderItems trong DB
           └─ 7. Gọi pay-service → tạo Payment record
           └─ 8. Gọi ship-service → tạo Shipment record (tracking number tự động)
           └─ 9. Gọi book-service → giảm tồn kho
           └─ 10. Gọi cart-service → xóa giỏ hàng
           └─ 11. Cập nhật Order status = "confirmed"
           └─ Trả về { order, payment, shipment }
```

### Luồng 5 — Đánh giá sách
```
Customer → POST /api/reviews/  { book_id, rating, comment }
           └─ comment-service xác thực token qua customer-service
           └─ update_or_create Review (một customer 1 sách chỉ có 1 review)
```

### Luồng 6 — Gợi ý sách
```
Client → GET /api/recommendations/{customer_id}/
         └─ recommender-service lấy tất cả reviews từ comment-service
         └─ Lấy lịch sử mua của customer từ order-service
         └─ Tính score cho từng sách (loại trừ đã mua/đã đánh giá)
         └─ Lưu cache → trả về top 10
```

---

## 6. Mô hình dữ liệu chính

### staff-service
```
Staff: id, name, email, password(hashed), phone, role(staff/senior_staff), is_active, created_at
StaffToken: id, staff(FK), key(SHA256), created_at
```

### manager-service
```
Manager: id, name, email, password(hashed), phone, is_active, created_at
ManagerToken: id, manager(FK), key(SHA256), created_at
```

### customer-service
```
Customer: id, name, email, password(hashed), phone, address, is_active, created_at
CustomerToken: id, customer(FK), key(SHA256), created_at
```

### catalog-service
```
Category: id, name(unique), description, parent(self-FK nullable), created_at
```

### book-service
```
Book: id, title, author, isbn(unique), price, stock, category_id, category_name(snapshot),
      description, cover_url, is_active, created_by_staff_id, created_at, updated_at
```

### cart-service
```
Cart: id, customer_id(unique), created_at, updated_at
CartItem: id, cart(FK), book_id, book_title(snapshot), book_author(snapshot), price, quantity
```

### order-service
```
Order: id, customer_id, shipping_method_id, shipping_method_name, shipping_cost,
       payment_method_id, payment_method_name, subtotal, total_amount,
       status(pending/confirmed/shipping/delivered/cancelled), shipping_address, notes,
       created_at, updated_at
OrderItem: id, order(FK), book_id, book_title, book_author, price, quantity
```

### ship-service
```
ShippingMethod: id, name, description, cost, delivery_days, is_active
Shipment: id, order_id(unique), method(FK), method_name, status, shipping_address,
          tracking_number(auto UUID), estimated_delivery, created_at, updated_at
```

### pay-service
```
PaymentMethod: id, name, description, is_active
Payment: id, order_id(unique), method(FK), method_name, amount, status,
         transaction_id(auto UUID), notes, created_at, updated_at
```

### comment-rate-service
```
Review: id, customer_id, book_id, rating(1-5), comment, created_at, updated_at
        [unique_together: customer_id + book_id]
```

### recommender-ai-service
```
Recommendation: id, customer_id, book_id, score, reason, updated_at
                [unique_together: customer_id + book_id]
```
