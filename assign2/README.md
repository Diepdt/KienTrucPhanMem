# 📚 Django Bookstore - Assignment 2

## Domain Package MVC Architecture

Hệ thống quản lý cửa hàng sách trực tuyến được xây dựng theo kiến trúc **Domain Package MVC** với Django Framework.

---

## 🏗️ Kiến trúc hệ thống

```
store/
├── models/                          # Domain Models Layer
│   ├── book/
│   │   └── book.py                  # Book model
│   ├── customer/
│   │   ├── customer.py              # Customer model
│   │   └── rating.py                # Rating model
│   ├── staff/
│   │   └── staff.py                 # Staff model
│   └── order/
│       ├── cart.py                  # Cart model
│       ├── cart_item.py             # CartItem model
│       ├── order.py                 # Order, OrderItem models
│       ├── shipping.py              # Shipping model
│       └── payment.py               # Payment model
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

## 📊 Domain Models

### 1. Book Domain
| Model | Thuộc tính |
|-------|------------|
| **Book** | id, title, author, price, stock_quantity |

### 2. Customer Domain
| Model | Thuộc tính |
|-------|------------|
| **Customer** | id, name, email, password |
| **Rating** | customer (FK), book (FK), score (1-5) |

### 3. Staff Domain
| Model | Thuộc tính |
|-------|------------|
| **Staff** | id, name, email, password, role |

### 4. Order Domain
| Model | Thuộc tính |
|-------|------------|
| **Cart** | customer (FK), session_key |
| **CartItem** | cart (FK), book (FK), quantity |
| **Order** | customer (FK), shipping (FK), payment (FK), status, total_amount |
| **OrderItem** | order (FK), book (FK), quantity, price |
| **Shipping** | method, address, city, postal_code, country, cost |
| **Payment** | method, amount, status, transaction_id |

---

## 🚀 Chức năng hệ thống

### 👤 Customer Features
- ✅ Đăng ký / Đăng nhập / Đăng xuất
- ✅ Xem danh sách sách
- ✅ Tìm kiếm sách (AJAX)
- ✅ Xem chi tiết sách
- ✅ Đánh giá sách (1-5 sao)
- ✅ Thêm sách vào giỏ hàng
- ✅ Quản lý giỏ hàng
- ✅ Đặt hàng (Checkout)
- ✅ Xem lịch sử đơn hàng
- ✅ **Gợi ý sách thông minh**

### 👨‍💼 Staff Features
- ✅ Đăng nhập Staff
- ✅ Dashboard tổng quan
- ✅ Quản lý sách (CRUD)
- ✅ Import sách hàng loạt
- ✅ Cập nhật tồn kho
- ✅ Quản lý đơn hàng
- ✅ Cập nhật trạng thái đơn hàng

---

## 🤖 Hệ thống gợi ý sách

Thuật toán **Advanced Recommendation System** kết hợp nhiều chiến lược:

| Chiến lược | Trọng số | Mô tả |
|------------|----------|-------|
| **Purchase History (CartItem)** | 3.0x | "Khách hàng đã thêm vào giỏ sách này cũng thêm..." |
| **Order History (OrderItem)** | 4.0x | "Khách hàng đã mua sách này cũng mua..." |
| **Rating Collaborative** | 2.0x × avg | "Người đánh giá cao sách này cũng thích..." |
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
cd c:\django\assign2

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Tạo dữ liệu mẫu (optional)
python manage.py shell
```

```python
# Trong Django shell - tạo dữ liệu mẫu
from store.models import Staff, Book, Customer

# Tạo Staff
Staff.objects.create(
    name='Admin',
    email='admin@bookstore.com',
    password='admin123',
    role='admin'
)

# Tạo Customer
Customer.objects.create(
    name='Test Customer',
    email='customer@test.com',
    password='customer123'
)

# Tạo Books
books_data = [
    {'title': 'Python Programming', 'author': 'John Smith', 'price': 29.99, 'stock_quantity': 50},
    {'title': 'Django for Beginners', 'author': 'William Vincent', 'price': 39.99, 'stock_quantity': 30},
    {'title': 'Clean Code', 'author': 'Robert Martin', 'price': 45.00, 'stock_quantity': 25},
    {'title': 'Design Patterns', 'author': 'Gang of Four', 'price': 55.00, 'stock_quantity': 20},
    {'title': 'The Pragmatic Programmer', 'author': 'David Thomas', 'price': 49.99, 'stock_quantity': 35},
]
for data in books_data:
    Book.objects.create(**data)

print("Sample data created!")
```

```bash
# Chạy server
python manage.py runserver
```

### Cài đặt với Docker

```bash
# Build và chạy containers
docker-compose up --build

# Chạy ở background
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng containers
docker-compose down
```

---

## 🌐 URLs

### Public URLs
| URL | Mô tả |
|-----|-------|
| `/books/` | Danh sách sách |
| `/books/<id>/` | Chi tiết sách |
| `/books/search/` | API tìm kiếm |

### Customer URLs
| URL | Mô tả |
|-----|-------|
| `/customer/register/` | Đăng ký |
| `/customer/login/` | Đăng nhập |
| `/customer/logout/` | Đăng xuất |
| `/customer/profile/` | Trang cá nhân |
| `/customer/orders/` | Lịch sử đơn hàng |

### Cart URLs
| URL | Mô tả |
|-----|-------|
| `/cart/` | Xem giỏ hàng |
| `/cart/add/<book_id>/` | Thêm vào giỏ |
| `/cart/update/<item_id>/` | Cập nhật số lượng |
| `/cart/remove/<item_id>/` | Xóa khỏi giỏ |
| `/cart/checkout/` | Thanh toán |

### Staff URLs
| URL | Mô tả |
|-----|-------|
| `/staff/login/` | Đăng nhập Staff |
| `/staff/dashboard/` | Dashboard |
| `/staff/books/` | Quản lý sách |
| `/staff/books/add/` | Thêm sách |
| `/staff/books/<id>/edit/` | Sửa sách |
| `/staff/books/<id>/delete/` | Xóa sách |
| `/staff/books/import/` | Import sách |
| `/staff/books/<id>/stock/` | Cập nhật tồn kho |
| `/staff/orders/` | Quản lý đơn hàng |

---

## 🔐 Tài khoản mẫu

### Staff Account
- **Email:** admin@bookstore.com
- **Password:** admin123

### Customer Account
- **Email:** customer@test.com
- **Password:** customer123

---

## 🐳 Docker Services

| Service | Port | Mô tả |
|---------|------|-------|
| **web** | 8000 | Django Application |
| **db** | 3306 | MySQL 8.0 Database |
| **nginx** | 80 | Nginx Reverse Proxy |

---

## 📁 File Structure

```
c:\django\assign2\
├── bookstore1/                      # Django Project Settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                           # Main Application
│   ├── models/                      # Domain Models
│   ├── controllers/                 # Controllers (Views)
│   ├── templates/                   # HTML Templates
│   ├── admin.py                     # Admin Registration
│   └── urls.py                      # URL Router
├── monolith/                        # Legacy Monolithic App (backup)
├── static/                          # Static Files
├── Dockerfile                       # Docker Image Config
├── docker-compose.yml               # Docker Services
├── requirements.txt                 # Python Dependencies
├── nginx.conf                       # Nginx Configuration
├── manage.py                        # Django CLI
└── README.md                        # This file
```

---

## 🧪 Testing

```bash
# Chạy tests
python manage.py test store

# Với coverage
coverage run manage.py test store
coverage report
```

---

## 📝 ERD (Entity Relationship Diagram)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Customer  │────<│   Rating    │>────│    Book     │
│─────────────│     │─────────────│     │─────────────│
│ id          │     │ customer_id │     │ id          │
│ name        │     │ book_id     │     │ title       │
│ email       │     │ score       │     │ author      │
│ password    │     └─────────────┘     │ price       │
└─────────────┘                         │ stock_qty   │
       │                                └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Cart     │────<│  CartItem   │>────│    Book     │
│─────────────│     │─────────────│     └─────────────┘
│ id          │     │ cart_id     │
│ customer_id │     │ book_id     │
│ session_key │     │ quantity    │
└─────────────┘     └─────────────┘

       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Order    │────<│  OrderItem  │>────│    Book     │
│─────────────│     │─────────────│     └─────────────┘
│ id          │     │ order_id    │
│ customer_id │     │ book_id     │
│ shipping_id │     │ quantity    │
│ payment_id  │     │ price       │
│ status      │     └─────────────┘
│ total       │
└─────────────┘
       │
       ├───────────────────────┐
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  Shipping   │         │   Payment   │
│─────────────│         │─────────────│
│ id          │         │ id          │
│ method      │         │ method      │
│ address     │         │ amount      │
│ city        │         │ status      │
│ cost        │         │ trans_id    │
└─────────────┘         └─────────────┘

┌─────────────┐
│    Staff    │
│─────────────│
│ id          │
│ name        │
│ email       │
│ password    │
│ role        │
└─────────────┘
```

---

## 📄 License

This project is created for educational purposes - **Assignment 2**.

---

## 👨‍💻 Author

**Student Project** - Domain Package MVC Architecture with Django

---

## 🔗 Quick Start

```bash
# 1. Di chuyển vào thư mục project
cd c:\django\assign2

# 2. Kích hoạt virtual environment (nếu có)
venv\Scripts\activate

# 3. Chạy migrations
python manage.py migrate

# 4. Chạy server
python manage.py runserver

# 5. Truy cập website
# http://127.0.0.1:8000/books/
```

**Enjoy! 🎉**
