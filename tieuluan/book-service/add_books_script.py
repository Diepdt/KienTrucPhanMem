import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_config.settings')
django.setup()

from book.models import Book

books = [
    {'title': 'Lập Trình Python Cơ Bản', 'author': 'Nguyễn Văn Lập', 'price': '125000.00', 'stock': 50, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Hướng dẫn chi tiết về lập trình Python từ cơ bản đến nâng cao.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'Django REST Framework Toàn Tập', 'author': 'Trần Đình Hiệu', 'price': '150000.00', 'stock': 35, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Tất cả những gì bạn cần biết về Django REST Framework.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'Cấu Trúc Dữ Liệu & Giải Thuật', 'author': 'Lê Minh Hoàng', 'price': '180000.00', 'stock': 45, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Sách luyện tập cấu trúc dữ liệu và giải thuật có phương pháp.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'JavaScript ES6+ - Hướng Dẫn Hoàn Chỉnh', 'author': 'Thái Nhân Hùng', 'price': '140000.00', 'stock': 40, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Học JavaScript hiện đại với ES6+.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'React.js - Xây Dựng Ứng Dụng Web Hiện Đại', 'author': 'Võ Quốc Thắng', 'price': '160000.00', 'stock': 38, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Học React.js từ cơ bản đến nâng cao.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'SQL & Database Design', 'author': 'Chu Hùng Cơ', 'price': '145000.00', 'stock': 42, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Thiết kế cơ sở dữ liệu tối ưu.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'Git & GitHub - Quản Lý Mã Nguồn Chuyên Nghiệp', 'author': 'Phạm Văn Sỹ', 'price': '95000.00', 'stock': 60, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Sử dụng Git và GitHub như một chuyên gia.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'Docker & Kubernetes - Containerization', 'author': 'Dương Văn Kiên', 'price': '175000.00', 'stock': 30, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Hướng dẫn toàn diện về Docker và Kubernetes.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'Clean Code - Viết Code Chất Lượng Cao', 'author': 'Robert C. Martin', 'price': '165000.00', 'stock': 37, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Nguyên tắc viết code sạch, dễ bảo trì.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
    {'title': 'RESTful API Design - Thiết Kế API Chuẩn Mực', 'author': 'Hồ Quỳnh Hương', 'price': '130000.00', 'stock': 48, 'category_id': 1, 'category_name': 'Công Nghệ - Lập Trình', 'description': 'Thiết kế RESTful API chuyên nghiệp.', 'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900', 'is_active': True},
]

count = 0
for b in books:
    if not Book.objects.filter(title=b['title'], author=b['author']).exists():
        Book.objects.create(**b)
        print(f"✓ {b['title']}")
        count += 1
    else:
        print(f"⊘ Đã tồn tại: {b['title']}")

print(f"\n✓ Tổng cộng thêm {count} cuốn sách!")
