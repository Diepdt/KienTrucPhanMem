# 📚 Django Bookstore - E-Commerce System

## Domain Package MVC Architecture

Hệ thống quản lý cửa hàng sách trực tuyến được xây dựng theo kiến trúc **Domain Package MVC** với Django Framework.

**Tổng số lớp nghiệp vụ: 23 classes**

---

## 🏗️ Kiến trúc hệ thống

```
store/
├── models/                          # Domain Models Layer (23 Business Classes)
│   │
│   ├── book/                        # Book Domain (4 classes)
│   │   ├── book.py                  # Book model
│   │   ├── category.py              # Category model
│   │   ├── author.py                # Author model
│   │   └── publisher.py             # Publisher model
│   │
│   ├── customer/                    # Customer Domain (5 classes)
│   │   ├── customer.py              # Customer model
│   │   ├── address.py               # Address model
│   │   ├── rating.py                # Rating model
│   │   ├── review.py                # Review model
│   │   └── wishlist.py              # Wishlist, WishlistItem models
│   │
│   ├── staff/                       # Staff Domain (1 class)
│   │   └── staff.py                 # Staff model
│   │
│   ├── order/                       # Order Domain (8 classes)
│   │   ├── cart.py                  # Cart model
│   │   ├── cart_item.py             # CartItem model
│   │   ├── order.py                 # Order, OrderItem models
│   │   ├── shipping.py              # Shipping model
│   │   ├── payment.py               # Payment model
│   │   ├── order_history.py         # OrderHistory model
│   │   └── refund.py                # Refund model
│   │
│   ├── promotion/                   # Promotion Domain (2 classes)
│   │   ├── promotion.py             # Promotion model
│   │   └── coupon.py                # Coupon model
│   │
│   ├── inventory/                   # Inventory Domain (2 classes)
│   │   └── inventory.py             # Inventory, InventoryLog models
│   │
│   └── notification/                # Notification Domain (1 class)
│       └── notification.py          # Notification model
│
├── controllers/                     # Controllers Layer (Views)
│   ├── bookController/
│   │   ├── views.py                 # Book views
│   │   └── urls.py                  # Book URLs
│   ├── customerController/
│   │   ├── views.py                 # Customer views
│   │   └── urls.py                  # Customer URLs
│   ├── staffController/
│   │   ├── views.py                 # Staff views
│   │   └── urls.py                  # Staff URLs
│   └── orderController/
│       ├── views.py                 # Order/Cart views
│       └── urls.py                  # Order URLs
│
└── templates/                       # Views Layer (Templates)
    ├── base.html                    # Base template
    ├── book/                        # Book templates
    ├── cart/                        # Cart templates
    ├── customer/                    # Customer templates
    └── staff/                       # Staff templates
```

---

## 📊 Domain Models - 23 Business Classes

### 1. 📖 Book Domain (4 classes)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Book** | id, title, author, author_obj (FK), publisher (FK), category (FK), isbn, description, price, stock_quantity, pages, publication_date | Sản phẩm sách |
| **Category** | id, type | Danh mục sách |
| **Author** | id, name, biography, birth_date, email, website | Tác giả |
| **Publisher** | id, name, address, city, country, website, email, phone, founded_year | Nhà xuất bản |

### 2. 👤 Customer Domain (5 classes)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Customer** | id, name, email, password | Khách hàng |
| **Address** | id, num, street, city, customer (FK 1-1) | Địa chỉ khách hàng |
| **Rating** | id, score, comment, created_at, customer (FK), book (FK) | Đánh giá nhanh |
| **Review** | id, customer (FK), book (FK), title, content, rating, is_verified_purchase, helpful_votes, is_approved | Đánh giá chi tiết |
| **Wishlist** | id, customer (FK 1-1), name, is_public | Danh sách yêu thích |
| **WishlistItem** | id, wishlist (FK), book (FK), priority, notes | Sản phẩm trong wishlist |

### 3. 👨‍💼 Staff Domain (1 class)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Staff** | id, name, email, password, role | Nhân viên (admin/manager/clerk) |

### 4. 📦 Order Domain (8 classes)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Cart** | id, customer (FK), session_key, created_at | Giỏ hàng |
| **CartItem** | id, cart (FK), book (FK), quantity | Sản phẩm trong giỏ |
| **Order** | id, customer (FK), staff (FK), shipping (FK), payment (FK), status, total, notes | Đơn hàng |
| **OrderItem** | id, order (FK), book (FK), quantity, price | Sản phẩm trong đơn |
| **Shipping** | id, method, address, city, country, cost | Thông tin giao hàng |
| **Payment** | id, method, amount, status, transaction_id | Thanh toán |
| **OrderHistory** | id, order (FK), old_status, new_status, changed_by (FK), notes | Lịch sử trạng thái đơn |
| **Refund** | id, order (FK), amount, reason, status, processed_by (FK) | Hoàn tiền |

### 5. 🎁 Promotion Domain (2 classes)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Promotion** | id, name, description, discount_type, discount_percent, discount_amount, start_date, end_date, is_active, min_order_amount, max_uses | Chương trình khuyến mãi |
| **Coupon** | id, code, discount_type, discount_percent, discount_amount, valid_from, valid_to, max_uses, min_order_amount | Mã giảm giá |

### 6. 📦 Inventory Domain (2 classes)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Inventory** | id, book (FK 1-1), quantity, reorder_level, reorder_quantity, location, last_restocked | Quản lý tồn kho |
| **InventoryLog** | id, inventory (FK), action, quantity, notes, performed_by (FK) | Log xuất/nhập kho |

### 7. 🔔 Notification Domain (1 class)

| Class | Attributes | Description |
|-------|------------|-------------|
| **Notification** | id, recipient_type, customer (FK), staff (FK), title, message, notification_type, is_read, related_order (FK) | Thông báo hệ thống |

---

## 📈 Class Diagram Summary

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO BOOKSTORE - 23 BUSINESS CLASSES                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐  │
│  │   📖 BOOK DOMAIN     │    │   👤 CUSTOMER DOMAIN │    │   👨‍💼 STAFF DOMAIN   │  │
│  │   (4 classes)        │    │   (5 classes)        │    │   (1 class)          │  │
│  │──────────────────────│    │──────────────────────│    │──────────────────────│  │
│  │ • Book               │    │ • Customer           │    │ • Staff              │  │
│  │ • Category           │    │ • Address            │    └──────────────────────┘  │
│  │ • Author             │    │ • Rating             │                               │
│  │ • Publisher          │    │ • Review             │    ┌──────────────────────┐  │
│  └──────────────────────┘    │ • Wishlist           │    │   🎁 PROMOTION       │  │
│                              │ • WishlistItem       │    │   (2 classes)        │  │
│  ┌──────────────────────┐    └──────────────────────┘    │──────────────────────│  │
│  │   📦 ORDER DOMAIN    │                                │ • Promotion          │  │
│  │   (8 classes)        │    ┌──────────────────────┐    │ • Coupon             │  │
│  │──────────────────────│    │   📦 INVENTORY       │    └──────────────────────┘  │
│  │ • Cart               │    │   (2 classes)        │                               │
│  │ • CartItem           │    │──────────────────────│    ┌──────────────────────┐  │
│  │ • Order              │    │ • Inventory          │    │   🔔 NOTIFICATION    │  │
│  │ • OrderItem          │    │ • InventoryLog       │    │   (1 class)          │  │
│  │ • Shipping           │    └──────────────────────┘    │──────────────────────│  │
│  │ • Payment            │                                │ • Notification       │  │
│  │ • OrderHistory       │                                └──────────────────────┘  │
│  │ • Refund             │                                                          │
│  └──────────────────────┘                                                          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Chức năng hệ thống

### 👤 Customer Features
- ✅ Đăng ký / Đăng nhập / Đăng xuất
- ✅ Xem danh sách sách
- ✅ Tìm kiếm sách (AJAX)
- ✅ Xem chi tiết sách
- ✅ Đánh giá sách (Rating 1-5 sao)
- ✅ Viết review chi tiết
- ✅ Quản lý Wishlist
- ✅ Thêm sách vào giỏ hàng
- ✅ Quản lý giỏ hàng
- ✅ Áp dụng mã giảm giá (Coupon)
- ✅ Đặt hàng (Checkout)
- ✅ Xem lịch sử đơn hàng
- ✅ Yêu cầu hoàn tiền (Refund)
- ✅ Nhận thông báo

### 👨‍💼 Staff Features
- ✅ Đăng nhập Staff
- ✅ Dashboard tổng quan
- ✅ Quản lý sách (CRUD)
- ✅ Quản lý tác giả, nhà xuất bản
- ✅ Import sách hàng loạt
- ✅ Quản lý tồn kho (Inventory)
- ✅ Quản lý đơn hàng
- ✅ Xử lý hoàn tiền
- ✅ Tạo khuyến mãi, mã giảm giá
- ✅ Gửi thông báo

---

## 🤖 Hệ thống gợi ý sách

Thuật toán **Advanced Recommendation System** kết hợp nhiều chiến lược:

| Chiến lược | Trọng số | Mô tả |
|------------|----------|-------|
| **Purchase History (CartItem)** | 3.0x | "Khách hàng đã thêm vào giỏ sách này cũng thêm..." |
| **Order History (OrderItem)** | 4.0x | "Khách hàng đã mua sách này cũng mua..." |
| **Rating Collaborative** | 2.0x × avg | "Người đánh giá cao sách này cũng thích..." |
| **Review-based** | 3.0x | Dựa trên các review tích cực |
| **Popular Fallback** | 0.5x | Sách phổ biến (khi không đủ dữ liệu) |

---

## 🛠️ Cài đặt

### Yêu cầu
- Python 3.10+
- Django 5.0+
- MySQL 8.0 (hoặc SQLite cho development)

### Cài đặt thủ công

```bash
# Clone repository
cd c:\django\asso1.1

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py makemigrations
python manage.py migrate

# Chạy server
python manage.py runserver
```

### Cài đặt với Docker

```bash
# Build và chạy containers
docker-compose up --build

# Chạy ở background
docker-compose up -d

# Dừng containers
docker-compose down
```

---

## 📁 Cấu trúc thư mục

```
c:\django\asso1.1\
├── bookstore1/                      # Django Project Settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                           # Main Application (23 Business Classes)
│   ├── models/                      # Domain Models
│   │   ├── book/                    # 4 classes
│   │   ├── customer/                # 5 classes  
│   │   ├── staff/                   # 1 class
│   │   ├── order/                   # 8 classes
│   │   ├── promotion/               # 2 classes
│   │   ├── inventory/               # 2 classes
│   │   └── notification/            # 1 class
│   ├── controllers/                 # Controllers (Views)
│   ├── templates/                   # HTML Templates
│   ├── admin.py                     # Admin Registration
│   └── urls.py                      # URL Router
├── static/                          # Static Files
├── diagram/                         # UML Diagrams
├── Dockerfile                       # Docker Image Config
├── docker-compose.yml               # Docker Services
├── requirements.txt                 # Python Dependencies
├── nginx.conf                       # Nginx Configuration
├── manage.py                        # Django CLI
└── README.md                        # This file
```

---

## 🐳 Docker Services

| Service | Port | Mô tả |
|---------|------|-------|
| **web** | 8000 | Django Application |
| **db** | 3306 | MySQL 8.0 Database |
| **nginx** | 80 | Nginx Reverse Proxy |

---

## 📝 ERD (Entity Relationship Diagram)

```
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Author    │────<───────────────│    Book     │───────────────>────│  Publisher  │
│─────────────│                    │─────────────│                    │─────────────│
│ id          │                    │ id          │                    │ id          │
│ name        │                    │ title       │                    │ name        │
│ biography   │                    │ author_obj  │                    │ address     │
│ birth_date  │                    │ publisher   │                    │ city        │
│ email       │                    │ category    │                    │ country     │
└─────────────┘                    │ isbn        │                    │ website     │
                                   │ price       │                    └─────────────┘
                                   │ stock_qty   │
                                   └─────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │                                │                                │
         ▼                                ▼                                ▼
┌─────────────┐                    ┌─────────────┐                 ┌─────────────┐
│  Category   │                    │   Review    │                 │  Inventory  │
│─────────────│                    │─────────────│                 │─────────────│
│ id          │                    │ customer_id │                 │ book_id     │
│ type        │                    │ book_id     │                 │ quantity    │
└─────────────┘                    │ title       │                 │ reorder_lvl │
                                   │ content     │                 │ location    │
                                   │ rating      │                 └─────────────┘
                                   │ is_approved │                        │
                                   └─────────────┘                        ▼
                                                                   ┌─────────────┐
┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │InventoryLog │
│  Customer   │────<│   Rating    │>────│    Book     │           │─────────────│
│─────────────│     │─────────────│     └─────────────┘           │ inventory_id│
│ id          │     │ customer_id │                               │ action      │
│ name        │     │ book_id     │                               │ quantity    │
│ email       │     │ score       │                               └─────────────┘
│ password    │     └─────────────┘
└─────────────┘
       │
       ├──────────────────────────┬──────────────────────────┐
       │                          │                          │
       ▼                          ▼                          ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  Wishlist   │            │    Cart     │            │   Address   │
│─────────────│            │─────────────│            │─────────────│
│ customer_id │            │ customer_id │            │ customer_id │
│ name        │            │ session_key │            │ num, street │
│ is_public   │            └─────────────┘            │ city        │
└─────────────┘                   │                   └─────────────┘
       │                          │
       ▼                          ▼
┌─────────────┐            ┌─────────────┐
│WishlistItem │            │  CartItem   │
│─────────────│            │─────────────│
│ wishlist_id │            │ cart_id     │
│ book_id     │            │ book_id     │
│ priority    │            │ quantity    │
└─────────────┘            └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Order    │────<│  OrderItem  │     │  Shipping   │     │   Payment   │
│─────────────│     │─────────────│     │─────────────│     │─────────────│
│ customer_id │     │ order_id    │     │ method      │     │ method      │
│ shipping_id │     │ book_id     │     │ address     │     │ amount      │
│ payment_id  │     │ quantity    │     │ city        │     │ status      │
│ staff_id    │     │ price       │     │ cost        │     │ trans_id    │
│ status      │     └─────────────┘     └─────────────┘     └─────────────┘
│ total       │
└─────────────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│OrderHistory │            │   Refund    │            │    Staff    │
│─────────────│            │─────────────│            │─────────────│
│ order_id    │            │ order_id    │            │ id          │
│ old_status  │            │ amount      │            │ name        │
│ new_status  │            │ reason      │            │ email       │
│ changed_by  │            │ status      │            │ password    │
└─────────────┘            │ processed_by│            │ role        │
                           └─────────────┘            └─────────────┘

┌─────────────┐            ┌─────────────┐
│  Promotion  │            │   Coupon    │
│─────────────│            │─────────────│
│ name        │            │ code        │
│ discount_%  │            │ discount_%  │
│ start_date  │            │ valid_from  │
│ end_date    │            │ valid_to    │
│ is_active   │            │ max_uses    │
└─────────────┘            └─────────────┘

┌──────────────┐
│ Notification │
│──────────────│
│ recipient    │
│ customer_id  │
│ staff_id     │
│ title        │
│ message      │
│ type         │
│ is_read      │
└──────────────┘
```

---

## 📄 License

This project is created for educational purposes.

---

## 👨‍💻 Author

**Student Project** - Domain Package MVC Architecture with Django

**Total Business Classes: 23**

---

## 🔗 Quick Start

```bash
# 1. Di chuyển vào thư mục project
cd c:\django\asso1.1

# 2. Kích hoạt virtual environment (nếu có)
venv\Scripts\activate

# 3. Chạy migrations
python manage.py makemigrations
python manage.py migrate

# 4. Chạy server
python manage.py runserver

# 5. Truy cập website
# http://127.0.0.1:8000/
```

**Enjoy! 🎉**
