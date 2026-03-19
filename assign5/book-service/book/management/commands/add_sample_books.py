from django.core.management.base import BaseCommand
from book.models import Book


class Command(BaseCommand):
    help = 'Thêm 10 cuốn sách tương tự vào database'

    def handle(self, *args, **options):
        books_data = [
            {
                'title': 'Lập Trình Python Cơ Bản',
                'author': 'Nguyễn Văn Lập',
                'price': '125000.00',
                'stock': 50,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Hướng dẫn chi tiết về lập trình Python từ cơ bản đến nâng cao. Phù hợp cho người mới bắt đầu.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'Django REST Framework Toàn Tập',
                'author': 'Trần Đình Hiệu',
                'price': '150000.00',
                'stock': 35,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Tất cả những gì bạn cần biết về Django REST Framework. Chi tiết, thực tiễn và dễ hiểu.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'Cấu Trúc Dữ Liệu & Giải Thuật',
                'author': 'Lê Minh Hoàng',
                'price': '180000.00',
                'stock': 45,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Sách luyện tập cấu trúc dữ liệu và giải thuật có phương pháp. Lý thuyết + bài tập thực hành.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'JavaScript ES6+ - Hướng Dẫn Hoàn Chỉnh',
                'author': 'Thái Nhân Hùng',
                'price': '140000.00',
                'stock': 40,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Học JavaScript hiện đại với ES6+. Async/Await, Promise, Module, Class, và nhiều hơn nữa.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'React.js - Xây Dựng Ứng Dụng Web Hiện Đại',
                'author': 'Võ Quốc Thắng',
                'price': '160000.00',
                'stock': 38,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Học React.js từ cơ bản đến nâng cao. Hooks, Context API, State Management, Performance Optimization.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'SQL & Database Design',
                'author': 'Chu Hùng Cơ',
                'price': '145000.00',
                'stock': 42,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Thiết kế cơ sở dữ liệu tối ưu. SQL nâng cao, Normalization, Index, Query Optimization.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'Git & GitHub - Quản Lý Mã Nguồn Chuyên Nghiệp',
                'author': 'Phạm Văn Sỹ',
                'price': '95000.00',
                'stock': 60,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Sử dụng Git và GitHub như một chuyên gia. Branching, Merging, Collaboration, Best Practices.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'Docker & Kubernetes - Containerization',
                'author': 'Dương Văn Kiên',
                'price': '175000.00',
                'stock': 30,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Hướng dẫn toàn diện về Docker và Kubernetes. Container, Orchestration, Deployment Strategies.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'Clean Code - Viết Code Chất Lượng Cao',
                'author': 'Robert C. Martin (Dịch: Nguyễn Tiến Dũng)',
                'price': '165000.00',
                'stock': 37,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Nguyên tắc viết code sạch, dễ bảo trì và dễ mở rộng. Naming, Functions, Comments, Error Handling.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
            {
                'title': 'RESTful API Design - Thiết Kế API Chuẩn Mực',
                'author': 'Hồ Quỳnh Hương',
                'price': '130000.00',
                'stock': 48,
                'category_id': 1,
                'category_name': 'Công Nghệ - Lập Trình',
                'description': 'Thiết kế RESTful API chuyên nghiệp. HTTP Methods, Status Codes, Versioning, Security, Documentation.',
                'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=900&auto=format&fit=crop',
                'is_active': True,
            },
        ]

        created_count = 0
        for book_data in books_data:
            # Kiểm tra xem cuốn sách đó đã tồn tại hay chưa (theo title + author)
            if not Book.objects.filter(title=book_data['title'], author=book_data['author']).exists():
                Book.objects.create(**book_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Thêm: {book_data['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"⊘ Đã tồn tại: {book_data['title']}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Tổng cộng thêm {created_count} cuốn sách mới!")
        )
