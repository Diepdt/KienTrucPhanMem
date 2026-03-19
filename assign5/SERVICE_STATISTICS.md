# THỐNG KÊ SERVICES - BOOKSTORE E-COMMERCE PLATFORM

## 1. TỔNG SỐ SERVICES TRONG DỰ ÁN

### ✅ Backend Services (13 services):
1. **staff-service** (port 8001) - Quản lý nhân viên
2. **manager-service** (port 8002) - Quản lý nhà quản lý
3. **customer-service** (port 8003) - Quản lý khách hàng
4. **catalog-service** (port 8004) - Quản lý danh mục sản phẩm
5. **book-service** (port 8005) - Quản lý sách/sản phẩm
6. **cart-service** (port 8006) - Quản lý giỏ hàng
7. **order-service** (port 8007) - Quản lý đơn hàng
8. **ship-service** (port 8008) - Quản lý vận chuyển
9. **pay-service** (port 8009) - Quản lý thanh toán
10. **comment-rate-service** (port 8010) - Quản lý bình luận & đánh giá
11. **recommender-ai-service** (port 8011) - Hệ thống gợi ý sản phẩm (AI)
12. **agent-service** (port 8012) - Sales Agent thông minh (AI)
13. **cloth-service** (port 8013) - Quản lý hàng may mặc

### 🌐 Gateway & Infrastructure:
- **api-gateway** (port 8000) - Điểm vào duy nhất cho client (proxy)
- **mysql** (port 33306) - Database chung (14 databases riêng, 1 DB cho mỗi service)

**TOTAL: 15 services (13 business + 1 gateway + 1 database)**

---

## 2. SERVICES ĐÃ HOẠT ĐỘNG & HIỂN THỊ TRÊN UI

### 📊 TÍNH TOÁN:
- **Tổng services có route trong gateway**: 14 endpoints
- **Services thực sự được sử dụng trong UI hiện tại**: 9 services
- **Tỷ lệ sử dụng**: 64.3% (9/14)

### ✅ SERVICES ĐANG HOẠT ĐỘNG (9 services):

#### **CUSTOMER SIDE (Khách hàng):**
| Endpoint | Service | Chức năng | Trạng thái |
|----------|---------|----------|-----------|
| `/api/customers/` | **customer-service** | Đăng ký, đăng nhập, thông tin cá nhân | ✅ Hoạt động tốt |
| `/api/books/` | **book-service** | Danh sách sách, tìm kiếm, chi tiết sản phẩm | ✅ Hoạt động tốt |
| `/api/categories/` | **catalog-service** | Danh sách danh mục sản phẩm | ✅ Hoạt động tốt |
| `/api/carts/` | **cart-service** | Giỏ hàng, thêm/xóa sản phẩm, cập nhật số lượng | ✅ Hoạt động tốt |
| `/api/orders/` | **order-service** | Tạo đơn, lịch sử đơn, chi tiết đơn | ✅ Hoạt động tốt |
| `/api/shipping/` | **ship-service** | Phương thức vận chuyển | ✅ Hoạt động tốt |
| `/api/payment/` | **pay-service** | Phương thức thanh toán | ✅ Hoạt động tốt |

#### **ADMIN SIDE (Quản lý):**
| Endpoint | Service | Chức năng | Trạng thái |
|----------|---------|----------|-----------|
| `/api/staffs/` | **staff-service** | Quản lý nhân viên, đăng nhập staff | ✅ Hoạt động tốt |
| `/api/managers/` | **manager-service** | Quản lý manager, đăng nhập admin | ✅ Hoạt động tốt |
| `/api/books/` | **book-service** | Quản lý sản phẩm CRUD | ✅ Hoạt động tốt |
| `/api/categories/` | **catalog-service** | Quản lý danh mục CRUD | ✅ Hoạt động tốt |
| `/api/orders/` | **order-service** | Xem đơn hàng, cập nhật trạng thái | ✅ Hoạt động tốt |

### ❌ SERVICES CHƯA SỬ DỤNG TRÊN UI (5 services):

| Endpoint | Service | Lý do | Ghi chú |
|----------|---------|-------|---------|
| `/api/reviews/` | **comment-rate-service** | Chưa có UI cho bình luận/đánh giá | Có route trong gateway sẵn sàng |
| `/api/recommendations/` | **recommender-ai-service** | Chưa có UI cho gợi ý sản phẩm | Backend sẵn sàng |
| `/api/clothes/` | **cloth-service** | Hàng may mặc chưa được bán | Dự trữ cho tương lai |
| `/api/agent/` | **agent-service** | AI sales agent chưa tích hợp UI | Backend sẵn sàng |
| Catalog endpoints | **Chưa sử dụng hết** | Category chỉ đọc, chưa có CRUD full | Admin có thể quản lý categories |

---

## 3. PHÂN TÍCH TỪ NG TRONG GATEWAY

```python
ROUTE_TABLE = [
    ('staffs/',         staff-service),          # ✅ Dùng
    ('staff/',          staff-service),          # ✅ Dùng
    ('managers/',       manager-service),        # ✅ Dùng
    ('manager/',        manager-service),        # ✅ Dùng
    ('customers/',      customer-service),       # ✅ Dùng
    ('categories/',     catalog-service),        # ✅ Dùng
    ('books/',          book-service),           # ✅ Dùng
    ('carts/',          cart-service),           # ✅ Dùng
    ('orders/',         order-service),          # ✅ Dùng
    ('shipping/',       ship-service),           # ✅ Dùng
    ('payment/',        pay-service),            # ✅ Dùng
    ('reviews/',        comment-rate-service),   # ❌ Chưa dùng
    ('recommendations/', recommender-ai-service),# ❌ Chưa dùng
    ('clothes/',        cloth-service),          # ❌ Chưa dùng
    ('agent/',          agent-service),          # ❌ Chưa dùng
]
```

---

## 4. KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
│  Customer Portal | Admin Dashboard | Login                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP/HTTPS
                         │
        ┌────────────────▼────────────────┐
        │      API Gateway (8000)          │
        │   - Routing & Proxy              │
        │   - Authentication               │
        │   - Request forwarding           │
        └────┬──────┬──────┬──────┬────┬───┘
             │      │      │      │    │
    ┌────────┘      │      │      │    │
    │         ┌─────┘      │      │    │
    │         │      ┌─────┘      │    │
    │         │      │      ┌─────┘    │
    │         │      │      │     ┌────┘
    │         │      │      │     │
    ▼         ▼      ▼      ▼     ▼
Staff-S   Manager Custome  Book  Cart
(8001)    (8002)  (8003)  (8005) (8006)
    │         │      │      │     │
    │         │      └──────────┬─┘
    │         │                 │
    ▼         ▼                 ▼
      Catalog │           Order
      (8004)  │          (8007)
              │             │
              │       ┌─────┼─────┐
              │       │     │     │
              ▼       ▼     ▼     ▼
           Payment  Ship  Comment Recommend AI
           (8009)  (8008) (8010)  (8011) Cloth
                                  (8013)
                                   │
                                   ▼
              ┌──────────────────────────┐
              │   MySQL (Shared DB)      │
              │  - 14 databases riêng    │
              │  - Replicated config     │
              └──────────────────────────┘
```

---

## 5. TRẠNG THÁI TỪNG COMPONENT

### 📱 Customer Interface Status:
- ✅ Home page (hiển thị sách nổi bật)
- ✅ Product listing & search (by title + author)
- ✅ Product detail
- ✅ Shopping cart (với checkbox chọn items)
- ✅ Checkout (chọn vận chuyển + thanh toán)
- ✅ Order history
- ✅ Profile (edit info)
- ✅ Login/Register
- ❌ Product reviews/comments
- ❌ Product recommendations
- ❌ Wishlist
- ❌ AI recommendation

### 🛠️ Admin Interface Status:
- ✅ Dashboard (với charts thống kê)
- ✅ User Management (add/ban/unban/edit)
- ✅ Product Management (CRUD sách)
- ✅ Category Management (CRUD danh mục)
- ✅ Order Management (view/sort/update status)
- ✅ Profile (edit info)
- ✅ Role-based access (Manager full, Staff limited)
- ❌ Sales reports
- ❌ Analytics
- ❌ Commission management

---

## 6. KẾT LUẬN

### 📊 Tóm tắt:
- **Tổng services**: 15 (13 backend + 1 gateway + 1 MySQL)
- **Services sử dụng hiện tại**: 9 services (64.3%)
- **Services sẵn sàng nhưng chưa dùng**: 5 services (comment, recommend, clothes, agent)
- **Số trang hiển thị**: 6+ pages (home, product, cart, checkout, orders, profile, admin dashboard, users, products, categories)
- **API endpoints hoạt động**: 9/14 routes trong gateway
- **Database**: 1 MySQL với 14 databases riêng

### 🚀 Các service sẵn sàng cho việc mở rộng:
1. **comment-rate-service** → Thêm reviews/ratings cho sản phẩm
2. **recommender-ai-service** → Gợi ý sản phẩm thông minh
3. **agent-service** → Sales chatbot AI
4. **cloth-service** → Thêm dòng sản phẩm may mặc

