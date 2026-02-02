# 📚 Django Bookstore - Assignment 3

## Enterprise E-Commerce Architecture with 52 Domain Models

Hệ thống quản lý cửa hàng sách trực tuyến được xây dựng theo kiến trúc **Domain Package MVC** với Django Framework và MySQL Database.

**📌 Yêu cầu chính:** 52 Models phân tích theo Class Diagram chuẩn

---

## 🏗️ Kiến trúc hệ thống

```
store/
├── models/                          # Domain Models Layer (52 Models)
│   ├── base.py                      # Abstract Models (2)
│   ├── user.py                      # Users & Roles (11)
│   ├── product.py                   # Products & Catalog (12)
│   ├── inventory.py                 # Inventory & Supply Chain (7)
│   ├── order.py                     # Sales & Orders (9)
│   ├── payment.py                   # Payment & Shipping (5)
│   └── marketing.py                 # Marketing & Content (6)
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

## 📊 Domain Models - 52 Classes

### 1. Abstract Models (2 classes) - `base.py`
| Model | Mô tả |
|-------|-------|
| **TimeStampedModel** | Abstract model với created_at, updated_at |
| **Person** | Abstract model với name, email, phone |

### 2. Users & Roles (11 classes) - `user.py`
| Model | Thuộc tính |
|-------|------------|
| **UserAccount** | username, email, password, is_active, is_staff |
| **Customer** | user (1-1), loyalty_points, member_tier |
| **CustomerProfile** | customer (1-1), avatar, date_of_birth, gender |
| **MemberTier** | name, discount_percent, min_points |
| **Staff** | user (1-1), employee_id, department |
| **Admin** | staff (1-1), permissions |
| **SalesStaff** | staff (1-1), sales_target |
| **WarehouseStaff** | staff (1-1), warehouse (FK) |
| **Shipper** | staff (1-1), vehicle_type, area |
| **GuestSession** | session_key, ip_address |
| **Address** | customer (FK), full_name, phone, street, city, is_default |

### 3. Products & Catalog (12 classes) - `product.py`
| Model | Thuộc tính |
|-------|------------|
| **Category** | name, parent (self FK), is_active |
| **Book** | isbn, title, authors (M2M), price, stock_quantity, publisher |
| **BookDetail** | book (1-1), description, pages, weight, dimensions |
| **BookImage** | book (FK), image, is_primary |
| **Author** | name, bio, avatar |
| **Translator** | name, language |
| **Publisher** | name, address, website |
| **Language** | name, code |
| **BookFormat** | name (hardcover, paperback, ebook) |
| **Series** | name, description |
| **Tag** | name, slug |
| **BookTag** | book (FK), tag (FK) |

### 4. Inventory & Supply Chain (7 classes) - `inventory.py`
| Model | Thuộc tính |
|-------|------------|
| **Supplier** | name, contact_person, email, phone |
| **Warehouse** | name, address, capacity |
| **Inventory** | book (FK), warehouse (FK), quantity |
| **ImportOrder** | supplier (FK), warehouse (FK), total, status |
| **ImportOrderItem** | import_order (FK), book (FK), quantity, unit_price |
| **StockTransfer** | from_warehouse, to_warehouse, quantity |
| **ReturnRequestToSupplier** | supplier (FK), reason, status |

### 5. Sales & Orders (9 classes) - `order.py`
| Model | Thuộc tính |
|-------|------------|
| **Cart** | customer (FK), session_key, is_active |
| **CartItem** | cart (FK), book (FK), quantity |
| **Order** | order_number, customer (FK), total, status |
| **OrderItem** | order (FK), book (FK), quantity, unit_price |
| **OrderStatusHistory** | order (FK), status, changed_by, notes |
| **Wishlist** | customer (FK), name |
| **WishlistItem** | wishlist (FK), book (FK) |
| **Review** | customer (FK), book (FK), title, content |
| **Rating** | customer (FK), book (FK), score (1-5) |

### 6. Payment & Shipping (5 classes) - `payment.py`
| Model | Thuộc tính |
|-------|------------|
| **PaymentMethod** | name, code, is_active |
| **Payment** | order (FK), payment_method (FK), amount, status |
| **ShippingMethod** | name, base_cost, estimated_days |
| **Shipment** | order (FK), tracking_number, status |
| **RefundRequest** | order (FK), reason, status, amount |

### 7. Marketing & Content (6 classes) - `marketing.py`
| Model | Thuộc tính |
|-------|------------|
| **Promotion** | name, discount_percent, start_date, end_date |
| **Coupon** | code, discount_amount, min_purchase, usage_limit |
| **Notification** | customer (FK), title, message, is_read |
| **Banner** | title, image, link, is_active |
| **BlogPost** | title, content, author (FK), status |
| **SystemConfig** | key, value, description |

---

## 🚀 Chức năng hệ thống

### 👤 Customer Features
- ✅ Đăng ký / Đăng nhập / Đăng xuất
- ✅ Xem danh sách sách (phân trang, sắp xếp)
- ✅ Tìm kiếm sách theo tên, tác giả, category
- ✅ Xem chi tiết sách
- ✅ Đánh giá sách (1-5 sao)
- ✅ Thêm sách vào giỏ hàng (AJAX)
- ✅ Quản lý giỏ hàng
- ✅ Checkout đặt hàng
- ✅ Xem lịch sử đơn hàng
- ✅ Quản lý địa chỉ giao hàng

### 👨‍💼 Staff Features
- ✅ Đăng nhập Staff
- ✅ Dashboard tổng quan
- ✅ Quản lý sách (CRUD)
- ✅ Import sách hàng loạt
- ✅ Cập nhật tồn kho
- ✅ Quản lý đơn hàng
- ✅ Cập nhật trạng thái đơn hàng

---

## 🛠️ Cài đặt

### Yêu cầu
- Python 3.11+
- Django 5.2+
- MySQL 8.0

### Cấu hình Database

```python
# bookstore1/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore_assign3',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Cài đặt thủ công

```bash
# Clone repository
cd c:\django\assign3

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo database MySQL
mysql -u root -p
CREATE DATABASE bookstore_assign3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# Chạy migrations
python manage.py migrate

# Seed dữ liệu mẫu
python seed_data.py

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

## 🌐 URLs

### Public URLs
| URL | Mô tả |
|-----|-------|
| `/books/` | Danh sách sách |
| `/books/<id>/` | Chi tiết sách |

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
| `/staff/orders/` | Quản lý đơn hàng |

---

## 🔐 Tài khoản mẫu

### Staff Account
- **Username:** admin
- **Password:** admin123

### Customer Accounts
| Email | Password |
|-------|----------|
| diepduong@gmail.com | hashed |
| nguyenvan@gmail.com | hashed |
| tranthib@gmail.com | hashed |

---

## 📚 Dữ liệu mẫu

### Sách Phật Giáo / Triết Học
- Đường Xưa Mây Trắng (Thích Nhất Hạnh)
- Thiền Giữa Đời Thường (Sayadaw U Tejaniya)
- Trong Sáng Như Pha Lê (Bhikkhu Bodhi)
- Tâm Bất Biến Giữa Dòng Đời (Ajahn Chah)
- Sự Im Lặng Của Thánh Nhân (Thích Nhất Hạnh)
- Sống Trong Tự Do (Ajahn Chah)

### Sách Self-Development
- Đắc Nhân Tâm (Dale Carnegie)
- Nhà Giả Kim (Paulo Coelho)
- Tư Duy Ngược (Nguyễn Anh Dũng)
- 7 Thói Quen Hiệu Quả (Stephen Covey)
- Atomic Habits (James Clear)
- Deep Work (Cal Newport)

### Văn Học Việt Nam
- Số Đỏ (Vũ Trọng Phụng)
- Chí Phèo (Nam Cao)
- Vang Bóng Một Thời (Nguyễn Tuân)
- Thương Nhớ Mười Hai (Vũ Bằng)
- Tắt Đèn (Ngô Tất Tố)
- Bước Đường Cùng (Nguyễn Công Hoan)

---

## 🐳 Docker Services

| Service | Port | Mô tả |
|---------|------|-------|
| **web** | 8000 | Django Application |
| **db** | 3306 | MySQL 8.0 Database |
| **nginx** | 80 | Nginx Reverse Proxy |

---

## 📁 Cấu trúc thư mục

```
c:\django\assign3\
├── bookstore1/                      # Django Project Settings
│   ├── settings.py                  # MySQL config
│   ├── urls.py
│   └── wsgi.py
├── store/                           # Main Application (52 Models)
│   ├── models/                      # Domain Models (7 files)
│   │   ├── __init__.py              # Exports all 52 models
│   │   ├── base.py                  # Abstract (2)
│   │   ├── user.py                  # Users (11)
│   │   ├── product.py               # Products (12)
│   │   ├── inventory.py             # Inventory (7)
│   │   ├── order.py                 # Orders (9)
│   │   ├── payment.py               # Payment (5)
│   │   └── marketing.py             # Marketing (6)
│   ├── controllers/                 # Controllers (Views)
│   ├── templates/                   # HTML Templates
│   ├── context_processors.py        # Cart count context
│   ├── admin.py                     # Admin Registration
│   └── urls.py                      # URL Router
├── static/                          # Static Files
├── seed_data.py                     # Database seeder
├── Dockerfile                       # Docker Image
├── docker-compose.yml               # Docker Services
├── requirements.txt                 # Dependencies
├── nginx.conf                       # Nginx Config
├── manage.py                        # Django CLI
└── README.md                        # Documentation
```

---

## 📄 License

This project is created for educational purposes - **Assignment 3**.

---

## 👨‍💻 Author

**Student Project** - Enterprise E-Commerce Architecture with 52 Domain Models

---

## 🔗 Quick Start

```bash
# 1. Di chuyển vào thư mục project
cd c:\django\assign3

# 2. Kích hoạt virtual environment
venv\Scripts\activate

# 3. Chạy server
python manage.py runserver

# 4. Truy cập website
# http://127.0.0.1:8000/books/
```

**Enjoy! 🎉**
