```markdown
# Software Architecture Assignment - Bookstore System

Dự án này là bài tập môn Kiến trúc phần mềm, mô phỏng hệ thống bán sách (Bookstore) được triển khai trên 3 mô hình kiến trúc khác nhau:
1. **Monolithic Architecture**
2. **Clean Architecture**
3. **Microservices Architecture**

## 🛠 Yêu cầu hệ thống (Prerequisites)

Trước khi chạy dự án, hãy đảm bảo máy tính của bạn đã cài đặt:
- **Python** (3.8 trở lên)
- **MySQL Server**
- **Git**

## ⚙️ Cài đặt chung

1. **Clone repository:**
   ```bash
   git clone <link-repo-cua-ban>
   cd kientrucphanmem

```

2. **Tạo và kích hoạt máy ảo (Virtual Environment):**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

```


3. **Cài đặt thư viện phụ thuộc:**
```bash
pip install django mysqlclient requests django-cors-headers

```


*(Lưu ý: Nếu cài `mysqlclient` bị lỗi trên Windows, hãy đảm bảo bạn đã cài C++ Build Tools hoặc tải file .whl tương ứng)*

---

## 🏛️ Version A: Monolithic Architecture

Phiên bản này gộp tất cả module (Customer, Book, Cart) vào một dự án Django duy nhất.

### Cách chạy:

1. **Tạo Database:**
Mở MySQL và chạy lệnh:
```sql
CREATE DATABASE monolith_db;

```


2. **Cấu hình Database:**
Mở file `monolith/bookstore1/settings.py`, tìm phần `DATABASES` và cập nhật `PASSWORD` MySQL của bạn.
3. **Di chuyển vào thư mục:**
```bash
cd monolith

```


4. **Migrate và chạy Server:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

```


5. **Truy cập:** `http://127.0.0.1:8000`

---

## 🧅 Version B: Clean Architecture

Phiên bản này phân chia dự án theo các tầng (Domain, Use Cases, Interfaces, Infrastructure) để tách biệt nghiệp vụ khỏi Framework.

### Cách chạy:

1. **Tạo Database:**
Mở MySQL và chạy lệnh:
```sql
CREATE DATABASE clean_db;

```


2. **Cấu hình Database:**
Mở file `clean/settings.py`, cập nhật thông tin kết nối trong phần `DATABASES`.
3. **Di chuyển vào thư mục:**
```bash
cd clean

```


4. **Migrate và chạy Server:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

```


5. **Truy cập:** `http://127.0.0.1:8000`

---

## 🌐 Version C: Microservices Architecture

Hệ thống được tách thành 3 dịch vụ độc lập, chạy trên 3 cổng (Port) khác nhau và giao tiếp qua REST API.

| Service | Port | Nhiệm vụ |
| --- | --- | --- |
| **Customer Service** | `8001` | Quản lý User (Đăng ký, Đăng nhập) |
| **Book Service** | `8002` | Quản lý Sách & Giao diện chính (Frontend) |
| **Cart Service** | `8003` | Quản lý Giỏ hàng |

### Cách chạy (Cần mở 3 cửa sổ Terminal riêng biệt):

#### Bước 1: Chuẩn bị Database

Mở MySQL và tạo 3 database riêng biệt:

```sql
CREATE DATABASE micro_customer_db;
CREATE DATABASE micro_book_db;
CREATE DATABASE micro_cart_db;

```

*Lưu ý: Vào `settings.py` của từng service trong thư mục `micro/` để cập nhật mật khẩu MySQL.*

#### Bước 2: Chạy Customer Service (Terminal 1)

```bash
cd micro/customer_service
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8001

```

#### Bước 3: Chạy Book Service (Terminal 2)

```bash
cd micro/book_service
python manage.py makemigrations
python manage.py migrate
# (Tùy chọn) Chạy lệnh SQL hoặc Admin để thêm sách mẫu vào DB
python manage.py runserver 8002

```

#### Bước 4: Chạy Cart Service (Terminal 3)

```bash
cd micro/cart_service
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8003

```

### Cách sử dụng:

* Truy cập vào **Book Service** tại: `http://127.0.0.1:8002`
* Khi bạn thực hiện hành động "Thêm vào giỏ", Book Service sẽ gọi API sang Cart Service (Port 8003) và Customer Service (Port 8001) để xử lý.

```

```
