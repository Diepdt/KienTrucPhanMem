# BÁO CÁO KỸ THUẬT
## ASSIGNMENT 05 — Triển Khai Microservices Hệ Thống EcomMart
### Django REST Framework + Docker Compose

---

**Môn học:** Lập trình Web / Hệ thống phân tán  
**Sinh viên:** [Họ tên sinh viên]  
**MSSV:** [Mã số sinh viên]  
**Ngày nộp:** Tháng 03/2026

---

## MỤC LỤC

1. [Giới thiệu tổng quan](#1-giới-thiệu-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Mô tả chi tiết từng service](#3-mô-tả-chi-tiết-từng-service)
4. [Giao tiếp giữa các service](#4-giao-tiếp-giữa-các-service)
5. [Mô hình dữ liệu](#5-mô-hình-dữ-liệu)
6. [Triển khai với Docker Compose](#6-triển-khai-với-docker-compose)
7. [Các luồng nghiệp vụ chính](#7-các-luồng-nghiệp-vụ-chính)
8. [Kết quả và đánh giá](#8-kết-quả-và-đánh-giá)
9. [Kết luận](#9-kết-luận)

---

## 1. GIỚI THIỆU TỔNG QUAN

### 1.1 Mục tiêu

Bài tập Assignment 05 yêu cầu phân rã hệ thống **EcomMart nguyên khối (monolithic)** thành kiến trúc **microservices** sử dụng Django REST Framework. Mỗi service hoạt động độc lập, có database riêng, giao tiếp với nhau qua REST API, và được triển khai thống nhất thông qua Docker Compose.

### 1.2 Phạm vi hệ thống

Hệ thống EcomMart bao gồm các chức năng cốt lõi:
- Quản lý nhân viên và phân quyền (staff, manager)
- Đăng ký / đăng nhập khách hàng
- Danh mục và quản lý sách
- Giỏ hàng tự động tạo khi đăng ký
- Đặt hàng tích hợp thanh toán và vận chuyển
- Đánh giá sách
- Gợi ý sách thông minh dựa trên AI

### 1.3 Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend framework | Django 4.2 + Django REST Framework 3.14 |
| Ngôn ngữ | Python 3.11 |
| Database | MySQL 8.0 (độc lập cho từng service) |
| Containerization | Docker + Docker Compose |
| Inter-service communication | HTTP REST (thư viện `requests`) |
| Authentication | Token-based (SHA-256 hash) |
| CORS | django-cors-headers |

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Sơ đồ kiến trúc tổng thể

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser / App)                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTP
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY  (Port 8000)                           │
│            ┌─────────────────────────────────────┐                   │
│            │     Proxy Router (ROUTE_TABLE)       │                   │
│            │  Prefix → Service URL mapping        │                   │
│            └─────────────────────────────────────┘                   │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──┘
   │      │      │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
:8001  :8002  :8003  :8004  :8005  :8006  :8007  :8008  :8009  :8010  :8011
staff  mgr   cust  catalog book  cart  order  ship   pay  comment recomm
  │      │      │      │      │      │      │      │      │      │      │
  ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
db_stf db_mgr db_cst db_cat db_bk db_crt db_ord db_shp db_pay db_cmt db_rec
```

### 2.2 Danh sách 12 Service

| # | Service | Port | Database | Chức năng chính |
|---|---------|------|----------|----------------|
| 1 | api-gateway | 8000 | SQLite | Proxy/định tuyến tất cả request từ client |
| 2 | staff-service | 8001 | db_staff | Quản lý nhân viên, xác thực staff token |
| 3 | manager-service | 8002 | db_manager | Quản lý cấp trên, phân quyền quản lý staff |
| 4 | customer-service | 8003 | db_customer | Đăng ký/đăng nhập/xác thực khách hàng |
| 5 | catalog-service | 8004 | db_catalog | Danh mục sách phân cấp (có sub-categories) |
| 6 | book-service | 8005 | db_book | CRUD sách (staff-only), tìm kiếm, quản lý tồn kho |
| 7 | cart-service | 8006 | db_cart | Giỏ hàng, tự tạo khi đăng ký |
| 8 | order-service | 8007 | db_order | Đặt hàng, điều phối payment + shipment |
| 9 | ship-service | 8008 | db_ship | Phương thức vận chuyển, theo dõi lô hàng |
| 10 | pay-service | 8009 | db_pay | Phương thức thanh toán, giao dịch |
| 11 | comment-rate-service | 8010 | db_comment | Đánh giá và chấm điểm sách |
| 12 | recommender-ai-service | 8011 | db_recommender | Gợi ý sách AI (content-based + popularity) |

### 2.3 Nguyên tắc thiết kế

**Database per service:** Mỗi service sở hữu một MySQL database riêng biệt, không service nào truy cập trực tiếp database của service khác. Dữ liệu được chia sẻ thông qua REST API hoặc dùng kỹ thuật **snapshot** (lưu lại bản sao tại thời điểm giao dịch, ví dụ: `book_title`, `category_name`).

**Single entry point:** Mọi request từ client đều đi qua **API Gateway** (port 8000). Gateway thực hiện proxy routing dựa trên URL prefix mà không xử lý logic nghiệp vụ.

**Token-based authentication:** Mỗi loại người dùng (Staff, Manager, Customer) có token riêng. Các service cần xác thực sẽ gọi đến service sở hữu token để verify, không chia sẻ secret key.

---

## 3. MÔ TẢ CHI TIẾT TỪNG SERVICE

### 3.1 API Gateway (Port 8000)

API Gateway đóng vai trò là **điểm vào duy nhất** của hệ thống. Nó không có DB riêng (dùng SQLite nhỏ cho Django admin) và không chứa logic nghiệp vụ.

**Cơ chế hoạt động:**
- Nhận request từ client tại `/api/<path>/`
- Tra cứu bảng `ROUTE_TABLE` để xác định service đích dựa trên prefix của `path`
- Chuyển tiếp toàn bộ request (method, headers, body, query params) đến service đích
- Trả lại response nguyên vẹn cho client

**Bảng định tuyến (ROUTE_TABLE):**
```
staffs/         → staff-service:8001
staff/          → staff-service:8001
managers/       → manager-service:8002
manager/        → manager-service:8002
customers/      → customer-service:8003
categories/     → catalog-service:8004
books/          → book-service:8005
carts/          → cart-service:8006
orders/         → order-service:8007
shipping/       → ship-service:8008
payment/        → pay-service:8009
reviews/        → comment-rate-service:8010
recommendations/ → recommender-ai-service:8011
```

**Xử lý lỗi:** Timeout (504), ConnectionError (503), lỗi khác (502).

**Health Check:** `GET /api/health/` kiểm tra khả năng kết nối đến tất cả 11 service và trả về trạng thái tổng thể.

---

### 3.2 Staff Service (Port 8001)

Quản lý thông tin nhân viên và cung cấp cơ chế xác thực token cho toàn hệ thống.

**Models:**
- `Staff`: name, email, password (SHA-256), phone, role (staff/senior_staff), is_active
- `StaffToken`: OneToOne với Staff, key được tạo bằng `SHA-256(os.urandom(32))`

**API Endpoints:**
- `GET /api/staffs/` — Danh sách nhân viên đang hoạt động
- `POST /api/staffs/` — Tạo nhân viên mới
- `PUT /api/staffs/{id}/` — Cập nhật thông tin
- `DELETE /api/staffs/{id}/` — Soft delete (đặt `is_active=False`)
- `POST /api/staff/login/` — Đăng nhập, trả về token
- `POST /api/staff/logout/` — Đăng xuất, xóa token
- `GET /api/staff/verify-token/` — Xác thực token (internal, gọi bởi book-service, manager-service)

---

### 3.3 Manager Service (Port 8002)

Quản lý cấp manager với khả năng điều phối nhân viên thông qua staff-service.

**Điểm đặc biệt:** `ManageStaffView` cho phép manager gọi staff-service để xem/tạo nhân viên, thể hiện pattern **manager-service làm proxy đến staff-service** — manager không cần biết địa chỉ nội bộ của staff-service.

---

### 3.4 Customer Service (Port 8003)

Quản lý vòng đời khách hàng. Khi đăng ký thành công, service tự động gọi cart-service để khởi tạo giỏ hàng trống, đảm bảo trải nghiệm liền mạch.

**Điểm đặc biệt:**
- `RegisterView`: Sau khi tạo Customer, gọi bất đồng bộ đến cart-service (`create_cart_for_customer`). Nếu cart-service lỗi, việc đăng ký vẫn thành công (không rollback) — đây là thiết kế **eventual consistency**.
- `VerifyTokenView`: Endpoint nội bộ được gọi bởi cart-service, order-service, comment-service để xác thực customer token.

---

### 3.5 Catalog Service (Port 8004)

Quản lý danh mục sách với cấu trúc **cây phân cấp** (tự tham chiếu).

**Model Category** có trường `parent` là ForeignKey đến chính nó (`ForeignKey('self', null=True)`), cho phép tạo cấu trúc da cấp như:
```
Văn học
  ├── Tiểu thuyết
  ├── Truyện ngắn
  └── Thơ ca
Khoa học
  ├── Vật lý
  └── Hóa học
```

`CategorySerializer` dùng `SerializerMethodField` để đệ quy trả về sub-categories lồng nhau.

---

### 3.6 Book Service (Port 8005)

Trung tâm quản lý sách. Phân quyền rõ ràng: staff có toàn quyền CRUD, còn khách hàng chỉ được đọc.

**Phân quyền:**
- Mọi request tạo/sửa/xóa sách đều verify staff token qua staff-service trước khi xử lý.
- Khi tạo sách, service tự động lấy `category_name` từ catalog-service và lưu vào trường snapshot, đảm bảo dữ liệu nhất quán ngay cả khi catalog-service tạm ngưng.

**UpdateStockView:** Endpoint nội bộ nhận danh sách `{book_id, quantity}` từ order-service, kiểm tra và giảm tồn kho theo từng cuốn sách trong đơn hàng.

---

### 3.7 Cart Service (Port 8006)

Quản lý giỏ hàng với logic xác thực kép: verify customer token qua customer-service và kiểm tra tồn kho qua book-service trước khi thêm sản phẩm.

**Hai loại endpoint:**
- **Public** (cần customer token): xem, thêm, sửa, xóa item
- **Internal** (không cần token, chỉ dành cho service nội bộ): `GET /carts/{id}/internal/` (order-service đọc) và `POST /carts/{id}/clear/` (order-service xóa sau khi đặt hàng)

**Cơ chế tồn tại:** Dùng `get_or_create` ở `CreateCartView` và `AddToCartView`, đảm bảo không tạo trùng giỏ hàng.

---

### 3.8 Order Service (Port 8007)

Service phức tạp nhất hệ thống, đóng vai trò **orchestrator** điều phối 5 service khác trong một quy trình đặt hàng.

**Luồng xử lý `POST /api/orders/create/`:**
1. Xác thực customer token (→ customer-service)
2. Lấy nội dung giỏ hàng (→ cart-service, internal endpoint)
3. Lấy thông tin phương thức vận chuyển (→ ship-service)
4. Lấy thông tin phương thức thanh toán (→ pay-service)
5. Tính `subtotal` + `shipping_cost` = `total_amount`
6. Tạo `Order` + `OrderItem` records trong DB
7. Tạo `Payment` record (→ pay-service)
8. Tạo `Shipment` record (→ ship-service)
9. Giảm tồn kho sách (→ book-service)
10. Xóa giỏ hàng (→ cart-service)
11. Cập nhật `Order.status = 'confirmed'`

---

### 3.9 Ship Service (Port 8008)

Quản lý phương thức vận chuyển và lô hàng. Mỗi `Shipment` được tự động gán `tracking_number` (định dạng `TRK-<UUID_12_chars>`) và tính `estimated_delivery` dựa trên `delivery_days` của phương thức vận chuyển.

**Trạng thái Shipment:** `pending → processing → shipped → delivered / failed / returned`

---

### 3.10 Pay Service (Port 8009)

Quản lý phương thức thanh toán và giao dịch. Mỗi `Payment` được tự động gán `transaction_id` (định dạng `PAY-<UUID_12_chars>`).

**Trạng thái Payment:** `pending → processing → completed / failed / refunded`

---

### 3.11 Comment & Rate Service (Port 8010)

Cho phép khách hàng đánh giá sách với điểm từ 1-5. Áp dụng quy tắc **một khách hàng chỉ có một đánh giá cho mỗi cuốn sách** (unique_together), sử dụng `update_or_create` để cập nhật nếu đã đánh giá trước đó.

**Endpoint nội bộ `AllReviewsInternalView`:** Trả về toàn bộ dữ liệu đánh giá (customer_id, book_id, rating) cho recommender-service sử dụng trong thuật toán gợi ý.

---

### 3.12 Recommender AI Service (Port 8011)

Hệ thống gợi ý sách dựa trên kết hợp hai phương pháp: **Content-based filtering** và **Popularity-based scoring**.

**Thuật toán `compute_recommendations(customer_id)`:**

```
1. Thu thập tất cả đánh giá từ comment-service (GET /reviews/all-internal/)
2. Tính avg_rating và review_count cho từng cuốn sách
3. Lấy lịch sử mua của customer từ order-service (GET /orders/customer/{id}/internal/)
4. Xây dựng tập "already_seen" = sách đã mua ∪ sách đã đánh giá
5. Tính popularity = review_count / max_review_count (normalize 0→1)
6. Score = avg_rating × 0.7 + popularity × 0.3 × 5  (scale về thang 0-5)
7. Lọc: chỉ giữ sách có avg_rating ≥ 3.5 và không có trong "already_seen"
8. Sắp xếp giảm dần theo score, lấy top 10
9. Lưu cache vào bảng Recommendation
```

**Cache mechanism:** Kết quả gợi ý được lưu vào DB (`Recommendation` table). `CachedRecommendationsView` phục vụ từ cache để tránh tính toán lại, chỉ tính lại khi cache rỗng.

---

## 4. GIAO TIẾP GIỮA CÁC SERVICE

### 4.1 Sơ đồ phụ thuộc

```
                    ┌─────────────────┐
                    │  staff-service  │◄──────────────────┐
                    └─────────────────┘                   │ verify token
                                                          │ manage staff
                    ┌─────────────────┐          ┌────────┴────────┐
                    │ catalog-service │◄──────────┤ manager-service │
                    └─────────────────┘ get cat   └─────────────────┘
                           │ name              
                           ▼                  
              ┌────────────────────────┐       ┌─────────────────┐
              │     book-service       │◄──────┤  customer needs │
              └────────────────────────┘ stock │  auth token     │
                           │ update    │       └─────────────────┘
                           │ stock     │         
                           ▼           │        ┌─────────────────┐
              ┌────────────────────────┐        │ customer-service│◄──────┐
              │    order-service       │────────►└─────────────────┘       │
              │  (orchestrator)        │          ▲ verify token            │
              └────────────────────────┘          │                         │ verify
                    │          │                  │                         │ token
                    ▼          ▼          ┌───────────────┐                │
             ┌──────────┐ ┌──────────┐   │ cart-service  │─────────────────┘
             │ship-svc  │ │pay-svc   │   └───────────────┘
             └──────────┘ └──────────┘         │ all reviews
                                               ▼
              ┌─────────────────────────────────────────────┐
              │         comment-rate-service                 │
              └─────────────────────────────────────────────┘
                                    ▲
              ┌─────────────────────┴─────────────────────┐
              │        recommender-ai-service              │
              │  (calls: comment, order, book, customer)   │
              └───────────────────────────────────────────┘
```

### 4.2 Bảng inter-service calls

| Caller | Callee | Endpoint | Mục đích |
|--------|--------|----------|----------|
| customer-service | cart-service | `POST /api/carts/create/` | Tự động tạo giỏ khi đăng ký |
| book-service | staff-service | `GET /api/staff/verify-token/` | Xác thực quyền staff |
| book-service | catalog-service | `GET /api/categories/{id}/` | Lấy tên danh mục |
| cart-service | customer-service | `GET /api/customers/verify-token/` | Xác thực token khách hàng |
| cart-service | book-service | `GET /api/books/{id}/` | Kiểm tra tồn kho |
| order-service | customer-service | `GET /api/customers/verify-token/` | Xác thực token |
| order-service | cart-service | `GET /api/carts/{id}/internal/` | Lấy nội dung giỏ hàng |
| order-service | cart-service | `POST /api/carts/{id}/clear/` | Xóa giỏ sau đặt hàng |
| order-service | ship-service | `GET /api/shipping/methods/{id}/` | Lấy thông tin ship method |
| order-service | ship-service | `POST /api/shipping/create/` | Tạo lô vận chuyển |
| order-service | pay-service | `GET /api/payment/methods/{id}/` | Lấy thông tin pay method |
| order-service | pay-service | `POST /api/payment/create/` | Tạo giao dịch thanh toán |
| order-service | book-service | `POST /api/books/update-stock/` | Cập nhật tồn kho |
| comment-service | customer-service | `GET /api/customers/verify-token/` | Xác thực token |
| manager-service | staff-service | `GET|POST /api/staffs/` | Quản lý nhân viên |
| recommender-service | comment-service | `GET /api/reviews/all-internal/` | Lấy tất cả đánh giá |
| recommender-service | order-service | `GET /api/orders/customer/{id}/internal/` | Lấy lịch sử mua |
| recommender-service | book-service | `GET /api/books/` | Lấy danh sách sách |

### 4.3 Xác thực token theo luồng

```
Client                 Gateway             book-service        staff-service
  │                       │                     │                    │
  │ POST /api/books/       │                     │                    │
  │ Authorization: Token X │                     │                    │
  ├──────────────────────►│                     │                    │
  │                       │ Proxy forward        │                    │
  │                       ├────────────────────►│                    │
  │                       │                     │ GET /verify-token/ │
  │                       │                     │ Authorization: X   │
  │                       │                     ├───────────────────►│
  │                       │                     │   {valid: true}    │
  │                       │                     │◄───────────────────┤
  │                       │                     │ Create book        │
  │                       │    Response 201      │                    │
  │                       │◄────────────────────┤                    │
  │    Response 201        │                     │                    │
  │◄──────────────────────┤                     │                    │
```

---

## 5. MÔ HÌNH DỮ LIỆU

### 5.1 Database staff_service (db_staff)

```
┌─────────────────────────────────────────────┐
│                   Staff                      │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ name         │ VARCHAR(255)                 │
│ email        │ VARCHAR(254) UNIQUE          │
│ password     │ VARCHAR(255) — SHA256 hash   │
│ phone        │ VARCHAR(20) nullable         │
│ role         │ ENUM(staff, senior_staff)    │
│ is_active    │ BOOLEAN default True         │
│ created_at   │ DATETIME auto_now_add        │
└──────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────┐
│                 StaffToken                   │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ staff_id     │ FK → Staff (OneToOne)        │
│ key          │ VARCHAR(64) UNIQUE           │
│ created_at   │ DATETIME auto_now_add        │
└──────────────┴──────────────────────────────┘
```

### 5.2 Database cart_service (db_cart)

```
┌─────────────────────────────────────────────┐
│                    Cart                      │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ customer_id  │ INT UNIQUE                   │
│ created_at   │ DATETIME auto_now_add        │
│ updated_at   │ DATETIME auto_now            │
└──────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────┐
│                  CartItem                    │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ cart_id      │ FK → Cart                    │
│ book_id      │ INT                          │
│ book_title   │ VARCHAR(255) snapshot        │
│ book_author  │ VARCHAR(255) snapshot        │
│ price        │ DECIMAL(10,2)                │
│ quantity     │ INT                          │
│ UNIQUE       │ (cart_id, book_id)           │
└──────────────┴──────────────────────────────┘
```

### 5.3 Database order_service (db_order)

```
┌─────────────────────────────────────────────────────┐
│                       Order                          │
├──────────────────────┬──────────────────────────────┤
│ id                   │ INT (PK, auto)               │
│ customer_id          │ INT                          │
│ shipping_method_id   │ INT                          │
│ shipping_method_name │ VARCHAR(100) snapshot        │
│ shipping_cost        │ DECIMAL(10,2)                │
│ payment_method_id    │ INT                          │
│ payment_method_name  │ VARCHAR(100) snapshot        │
│ subtotal             │ DECIMAL(10,2)                │
│ total_amount         │ DECIMAL(10,2)                │
│ status               │ ENUM(pending/confirmed/      │
│                      │   shipping/delivered/        │
│                      │   cancelled)                 │
│ shipping_address     │ TEXT                         │
│ notes                │ TEXT nullable                │
│ created_at           │ DATETIME auto_now_add        │
│ updated_at           │ DATETIME auto_now            │
└──────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────┐
│                 OrderItem                    │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ order_id     │ FK → Order                   │
│ book_id      │ INT                          │
│ book_title   │ VARCHAR(255) snapshot        │
│ book_author  │ VARCHAR(255) snapshot        │
│ price        │ DECIMAL(10,2) snapshot       │
│ quantity     │ INT                          │
└──────────────┴──────────────────────────────┘
```

### 5.4 Database comment_service (db_comment)

```
┌─────────────────────────────────────────────┐
│                   Review                     │
├──────────────┬──────────────────────────────┤
│ id           │ INT (PK, auto)               │
│ customer_id  │ INT                          │
│ book_id      │ INT                          │
│ rating       │ INT (1–5, validated)         │
│ comment      │ TEXT nullable                │
│ created_at   │ DATETIME auto_now_add        │
│ updated_at   │ DATETIME auto_now            │
│ UNIQUE       │ (customer_id, book_id)       │
└──────────────┴──────────────────────────────┘
```

---

## 6. TRIỂN KHAI VỚI DOCKER COMPOSE

### 6.1 Cấu trúc Docker

Mỗi service có cấu trúc Docker độc lập:
```
<service-name>/
├── Dockerfile          # Python 3.11-slim, cài deps, expose port
├── entrypoint.sh       # Chờ MySQL, makemigrations, migrate, runserver
├── requirements.txt    # Django, DRF, mysqlclient, requests...
├── manage.py
├── <app>/              # Django app: models, views, serializers, urls
└── <config>/           # settings.py, urls.py, wsgi.py
```

### 6.2 Entrypoint Script

```bash
#!/bin/bash
# Chờ MySQL khởi động xong
while ! python -c "import MySQLdb; MySQLdb.connect(host='$DB_HOST', \
    user='$DB_USER', passwd='$DB_PASSWORD', db='$DB_NAME')"; do
    sleep 1
done

python manage.py makemigrations --noinput   # Tạo migration files
python manage.py migrate --noinput          # Apply migrations
exec python manage.py runserver 0.0.0.0:<PORT>
```

### 6.3 Khởi tạo MySQL Database

File `mysql-init/init.sql` chạy tự động khi MySQL container khởi động lần đầu, tạo 11 databases riêng biệt:

```sql
CREATE DATABASE IF NOT EXISTS db_staff     CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_manager   CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_customer  CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_catalog   CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_book      CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_cart      CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_order     CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_ship      CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_pay       CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_comment   CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS db_recommender CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON db_* TO 'root'@'%';
```

### 6.4 Health Check và Service Dependencies

MySQL được cấu hình `healthcheck` trong docker-compose:
```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  retries: 10
```

Tất cả service chỉ khởi động khi MySQL `healthy`:
```yaml
depends_on:
  mysql:
    condition: service_healthy
```

### 6.5 Biến môi trường

Mỗi service nhận cấu hình qua environment variables, không hardcode:
```yaml
environment:
  DB_NAME: db_book
  DB_USER: root
  DB_PASSWORD: "123456"
  DB_HOST: mysql
  DB_PORT: "3306"
  SECRET_KEY: "book-secret-key-production"
  STAFF_SERVICE_URL: "http://staff-service:8001"
  CATALOG_SERVICE_URL: "http://catalog-service:8004"
```

---

## 7. CÁC LUỒNG NGHIỆP VỤ CHÍNH

### 7.1 Luồng đăng ký khách hàng → Tự động tạo giỏ hàng

```
Client                customer-service              cart-service
  │                        │                             │
  │ POST /customers/register/                            │
  │ {name, email, password} │                            │
  ├───────────────────────►│                            │
  │                        │ Validate + Hash password   │
  │                        │ Save Customer to db_cust   │
  │                        │                            │
  │                        │ POST /api/carts/create/    │
  │                        │ {customer_id: 5}           │
  │                        ├───────────────────────────►│
  │                        │                            │ Create Cart
  │                        │         201 Created        │ in db_cart
  │                        │◄───────────────────────────┤
  │                        │                            │
  │                        │ Generate CustomerToken     │
  │  201: {token, customer} │                            │
  │◄───────────────────────┤                            │
```

### 7.2 Luồng đặt hàng

```
Client          Gateway      order-service     customer   cart    pay   ship   book
  │               │               │              svc      svc     svc   svc    svc
  │POST/orders/   │               │               │        │       │     │      │
  │create/        │               │               │        │       │     │      │
  ├──────────────►│               │               │        │       │     │      │
  │               ├──────────────►│               │        │       │     │      │
  │               │               │verify token   │        │       │     │      │
  │               │               ├──────────────►│        │       │     │      │
  │               │               │  {valid:true} │        │       │     │      │
  │               │               │◄──────────────┤        │       │     │      │
  │               │               │get cart internal        │       │     │      │
  │               │               ├───────────────────────►│       │     │      │
  │               │               │   {cart+items}         │       │     │      │
  │               │               │◄───────────────────────┤       │     │      │
  │               │               │get ship method                  │     │      │
  │               │               ├────────────────────────────────►│     │      │
  │               │               │   {method, cost}               │     │      │
  │               │               │◄───────────────────────────────┤     │      │
  │               │               │get pay method                         │      │
  │               │               ├──────────────────────────────────────►│      │
  │               │               │  {method}                             │      │
  │               │               │◄──────────────────────────────────────┤      │
  │               │               │ Create Order + Items in db_order       │      │
  │               │               │create payment                          │      │
  │               │               ├──────────────────────────────────────►│      │
  │               │               │   {payment}                           │      │
  │               │               │◄──────────────────────────────────────┤      │
  │               │               │create shipment                               │
  │               │               ├─────────────────────────────────────────────►│
  │               │               │   {shipment}                                 │
  │               │               │◄─────────────────────────────────────────────┤
  │               │               │update stock                                        │
  │               │               ├───────────────────────────────────────────────────►│
  │               │               │   200 OK                                           │
  │               │               │◄───────────────────────────────────────────────────┤
  │               │               │clear cart                       │
  │               │               ├───────────────────────────────►│
  │               │               │ order.status = "confirmed"      │
  │  201:{order,  │               │                                 │
  │  payment,     │◄──────────────┤                                 │
  │  shipment}    │               │
  │◄──────────────┤
```

---

## 8. KẾT QUẢ VÀ ĐÁNH GIÁ

### 8.1 Đáp ứng yêu cầu Assignment 05

| Yêu cầu | Trạng thái | Ghi chú |
|---------|-----------|---------|
| **4.2 — 12 Services** | ✅ Hoàn thành | Đủ 12 service theo yêu cầu |
| **4.3.1** — Đăng ký tự động tạo cart | ✅ Hoàn thành | customer-service gọi cart-service |
| **4.3.2** — Staff quản lý sách | ✅ Hoàn thành | book-service verify qua staff-service |
| **4.3.3** — Thêm/xem/sửa giỏ hàng | ✅ Hoàn thành | 5 endpoints add/view/update/remove/clear |
| **4.3.4** — Order kích hoạt pay+ship | ✅ Hoàn thành | Customer chọn ship và pay method |
| **4.3.5** — Đánh giá sách | ✅ Hoàn thành | comment-rate-service, 1-5 sao |
| **4.4 — Django REST Framework** | ✅ Hoàn thành | Tất cả service dùng DRF |
| **4.4 — REST inter-service calls** | ✅ Hoàn thành | 17 luồng giao tiếp nội bộ |
| **4.4 — Docker Compose** | ✅ Hoàn thành | 13 containers + MySQL |
| **4.4 — Independent databases** | ✅ Hoàn thành | 11 MySQL database độc lập |

### 8.2 Các tính năng bổ sung vượt yêu cầu

| Tính năng | Mô tả |
|-----------|-------|
| API Gateway | Single entry point, proxy routing, health check |
| Recommender AI | Thuật toán gợi ý Content-based + Popularity với cache |
| Soft delete | Staff, book sử dụng `is_active` thay vì xóa cứng |
| Snapshot pattern | Lưu bản sao dữ liệu tại thời điểm giao dịch |
| Internal endpoints | Endpoints nội bộ riêng biệt để service gọi nhau |
| Tracking number | Tự động sinh mã tracking (TRK-UUID) và transaction ID (PAY-UUID) |
| Sub-categories | Danh mục phân cấp đệ quy |

### 8.3 Kiến trúc URL tổng hợp

| Nhóm | Endpoint | HTTP | Mô tả |
|------|----------|------|-------|
| Auth | `/api/staff/login/` | POST | Đăng nhập staff |
| Auth | `/api/customers/register/` | POST | Đăng ký + tạo cart |
| Auth | `/api/customers/login/` | POST | Đăng nhập customer |
| Sách | `/api/books/` | GET | Danh sách (có filter) |
| Sách | `/api/books/` | POST | Thêm sách (staff) |
| Sách | `/api/books/{id}/` | PUT\|DELETE | Sửa/xóa sách (staff) |
| Giỏ | `/api/carts/{id}/` | GET | Xem giỏ hàng |
| Giỏ | `/api/carts/add/` | POST | Thêm vào giỏ |
| Đơn | `/api/orders/create/` | POST | Đặt hàng |
| Đơn | `/api/orders/` | GET | Lịch sử đơn hàng |
| Ship | `/api/shipping/methods/` | GET | DS phương thức ship |
| Pay | `/api/payment/methods/` | GET | DS phương thức thanh toán |
| Review | `/api/reviews/` | POST | Đánh giá sách |
| Review | `/api/reviews/books/{id}/` | GET | Reviews của sách |
| AI | `/api/recommendations/{id}/` | GET | Gợi ý sách |
| System | `/api/health/` | GET | Kiểm tra hệ thống |

---

## 9. KẾT LUẬN

### 9.1 Tổng kết

Dự án đã thành công phân rã hệ thống **EcomMart từ monolithic sang kiến trúc microservices** với 12 service độc lập, mỗi service đảm nhận một trách nhiệm rõ ràng theo nguyên tắc **Single Responsibility**. Hệ thống đáp ứng đầy đủ 10/10 yêu cầu kỹ thuật và nghiệp vụ của Assignment 05.

Điểm nổi bật của thiết kế:
- **Database isolation**: 11 MySQL database hoàn toàn độc lập, không service nào truy cập DB của service khác.
- **Token-based auth**: Cơ chế xác thực phân tán — mỗi service tự quản lý token, các service khác xác thực qua REST call.
- **Snapshot data**: Dữ liệu giao dịch (giá sách, tên danh mục) được snapshot để đảm bảo tính nhất quán lịch sử.
- **Orchestration pattern**: order-service đóng vai trò orchestrator điều phối 5 service khác trong một luồng đặt hàng phức tạp.
- **AI Recommender**: Hệ thống gợi ý dựa trên dữ liệu thực tế từ reviews và order history, có cache để tối ưu hiệu năng.

### 9.2 Hướng phát triển

Nếu mở rộng hệ thống trong tương lai, có thể cải tiến:
- Thay `runserver` bằng **Gunicorn + Nginx** cho production
- Thêm **message queue** (RabbitMQ/Kafka) để xử lý bất đồng bộ
- Áp dụng **Circuit Breaker** để tránh cascading failure
- Tích hợp **JWT** thay token SHA-256
- Thêm **distributed tracing** (Jaeger/Zipkin)
- **Rate limiting** tại API Gateway

---

*Báo cáo này được viết cho Assignment 05 — Môn Lập trình Web / Hệ thống phân tán.*
