"""
Seed Data Script - Insert sample data into the bookstore database
Run with: python seed_data.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore1.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from decimal import Decimal
from django.utils import timezone
from django.utils.text import slugify
from store.models import (
    # Users
    UserAccount, Customer, CustomerProfile, MemberTier, Staff, Address,
    # Products
    Category, Book, BookDetail, Author, Publisher, Language, BookFormat, Tag,
    # Inventory
    Supplier, Warehouse, Inventory,
    # Payment & Shipping
    PaymentMethod, ShippingMethod,
    # Marketing
    Coupon, Promotion, Banner, SystemConfig,
)

def seed_member_tiers():
    """Create member tiers"""
    print("Creating member tiers...")
    tiers = [
        {'name': 'bronze', 'min_points': 0, 'discount_percentage': 0, 'description': 'Thành viên mới'},
        {'name': 'silver', 'min_points': 1000, 'discount_percentage': 5, 'description': 'Thành viên bạc - Giảm 5%'},
        {'name': 'gold', 'min_points': 5000, 'discount_percentage': 10, 'description': 'Thành viên vàng - Giảm 10%'},
        {'name': 'platinum', 'min_points': 10000, 'discount_percentage': 15, 'description': 'Thành viên bạch kim - Giảm 15%'},
    ]
    for tier in tiers:
        MemberTier.objects.get_or_create(name=tier['name'], defaults=tier)
    print(f"  Created {len(tiers)} member tiers")

def seed_languages():
    """Create languages"""
    print("Creating languages...")
    languages = [
        {'name': 'Tiếng Việt', 'code': 'vi'},
        {'name': 'English', 'code': 'en'},
        {'name': 'Pāli', 'code': 'pi'},
        {'name': 'Sanskrit', 'code': 'sa'},
    ]
    for lang in languages:
        Language.objects.get_or_create(code=lang['code'], defaults=lang)
    print(f"  Created {len(languages)} languages")

def seed_book_formats():
    """Create book formats"""
    print("Creating book formats...")
    formats = ['hardcover', 'paperback', 'ebook', 'audiobook']
    for fmt in formats:
        BookFormat.objects.get_or_create(name=fmt)
    print(f"  Created {len(formats)} book formats")

def seed_categories():
    """Create book categories"""
    print("Creating categories...")
    categories = [
        {'name': 'Tâm linh & Triết học', 'slug': 'tam-linh-triet-hoc', 'description': 'Sách về Phật giáo, thiền định, triết học phương Đông'},
        {'name': 'Phát triển bản thân', 'slug': 'phat-trien-ban-than', 'description': 'Sách về năng suất, tư duy, kỹ năng sống'},
        {'name': 'Văn học Việt Nam', 'slug': 'van-hoc-viet-nam', 'description': 'Văn học Việt Nam cổ điển và đương đại'},
        {'name': 'Công nghệ thông tin', 'slug': 'cong-nghe-thong-tin', 'description': 'Sách về lập trình, phần mềm, công nghệ'},
        {'name': 'Kinh tế & Kinh doanh', 'slug': 'kinh-te-kinh-doanh', 'description': 'Sách về kinh tế, tài chính, khởi nghiệp'},
    ]
    for cat in categories:
        Category.objects.get_or_create(slug=cat['slug'], defaults={**cat, 'is_active': True})
    print(f"  Created {len(categories)} categories")

def seed_authors():
    """Create authors"""
    print("Creating authors...")
    authors_data = [
        # Tâm linh & Triết học
        {'name': 'Bhikkhu Bodhi', 'nationality': 'Mỹ', 'biography': 'Tỳ-kheo người Mỹ, học giả Phật giáo Theravada nổi tiếng'},
        {'name': 'Walpola Rahula', 'nationality': 'Sri Lanka', 'biography': 'Tỳ-kheo và học giả Phật giáo Sri Lanka'},
        {'name': 'Tulku Urgyen Rinpoche', 'nationality': 'Tây Tạng', 'biography': 'Đại sư Phật giáo Tây Tạng'},
        {'name': 'Sayadaw U Tejaniya', 'nationality': 'Myanmar', 'biography': 'Thiền sư Myanmar nổi tiếng về chánh niệm'},
        {'name': 'Nguyễn Hiến Lê', 'nationality': 'Việt Nam', 'biography': 'Học giả, dịch giả nổi tiếng Việt Nam'},
        {'name': 'Thích Nhất Hạnh', 'nationality': 'Việt Nam', 'biography': 'Thiền sư, nhà văn, nhà hoạt động hòa bình'},
        {'name': 'Ajahn Chah', 'nationality': 'Thái Lan', 'biography': 'Thiền sư nổi tiếng hệ phái Forest Tradition'},
        
        # Phát triển bản thân
        {'name': 'Cal Newport', 'nationality': 'Mỹ', 'biography': 'Giáo sư khoa học máy tính, tác giả về năng suất'},
        {'name': 'Ryan Holiday', 'nationality': 'Mỹ', 'biography': 'Tác giả về triết học Khắc kỷ'},
        {'name': 'Nguyễn Anh Dũng', 'nationality': 'Việt Nam', 'biography': 'Tác giả sách phát triển bản thân'},
        {'name': 'Austin Kleon', 'nationality': 'Mỹ', 'biography': 'Tác giả và nghệ sĩ'},
        {'name': 'Robert Greene', 'nationality': 'Mỹ', 'biography': 'Tác giả về chiến lược và quyền lực'},
        {'name': 'Matthew Walker', 'nationality': 'Anh', 'biography': 'Giáo sư thần kinh học, chuyên gia về giấc ngủ'},
        {'name': 'Anders Ericsson', 'nationality': 'Thụy Điển', 'biography': 'Nhà tâm lý học về chuyên môn và hiệu suất'},
        
        # Văn học Việt Nam
        {'name': 'Nguyễn Tuân', 'nationality': 'Việt Nam', 'biography': 'Nhà văn lớn của văn học Việt Nam hiện đại'},
        {'name': 'Vũ Trọng Phụng', 'nationality': 'Việt Nam', 'biography': 'Nhà văn hiện thực phê phán'},
        {'name': 'Nguyễn Nhật Ánh', 'nationality': 'Việt Nam', 'biography': 'Nhà văn nổi tiếng với các tác phẩm cho thiếu nhi và tuổi mới lớn'},
        {'name': 'Bảo Ninh', 'nationality': 'Việt Nam', 'biography': 'Nhà văn, tác giả "Nỗi buồn chiến tranh"'},
        {'name': 'Vũ Bằng', 'nationality': 'Việt Nam', 'biography': 'Nhà văn, nhà báo nổi tiếng'},
    ]
    for author in authors_data:
        Author.objects.get_or_create(name=author['name'], defaults=author)
    print(f"  Created {len(authors_data)} authors")

def seed_publishers():
    """Create publishers"""
    print("Creating publishers...")
    publishers_data = [
        {'name': 'NXB Tri Thức', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbtrithuc.vn'},
        {'name': 'NXB Trẻ', 'address': 'TP. Hồ Chí Minh, Việt Nam', 'email': 'info@nxbtre.vn'},
        {'name': 'NXB Kim Đồng', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbkimdong.vn'},
        {'name': 'NXB Văn Học', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbvanhoc.vn'},
        {'name': 'NXB Hồng Đức', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbhongduc.vn'},
        {'name': 'NXB Tôn Giáo', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbtongiao.vn'},
        {'name': 'NXB Thế Giới', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nxbthegioi.vn'},
        {'name': 'Nhã Nam', 'address': 'Hà Nội, Việt Nam', 'email': 'info@nhanam.vn'},
        {'name': 'Alpha Books', 'address': 'Hà Nội, Việt Nam', 'email': 'info@alphabooks.vn'},
        {'name': 'First News', 'address': 'TP. Hồ Chí Minh, Việt Nam', 'email': 'info@firstnews.vn'},
    ]
    for pub in publishers_data:
        Publisher.objects.get_or_create(name=pub['name'], defaults=pub)
    print(f"  Created {len(publishers_data)} publishers")

def seed_books():
    """Create books"""
    print("Creating books...")
    
    # Get references
    cat_tamlinh = Category.objects.get(slug='tam-linh-triet-hoc')
    cat_phattrien = Category.objects.get(slug='phat-trien-ban-than')
    cat_vanhoc = Category.objects.get(slug='van-hoc-viet-nam')
    
    lang_vi = Language.objects.get(code='vi')
    lang_en = Language.objects.get(code='en')
    
    fmt_paperback = BookFormat.objects.get(name='paperback')
    
    pub_trithuc = Publisher.objects.get(name='NXB Tri Thức')
    pub_tre = Publisher.objects.get(name='NXB Trẻ')
    pub_nhanam = Publisher.objects.get(name='Nhã Nam')
    pub_alpha = Publisher.objects.get(name='Alpha Books')
    pub_vanhoc = Publisher.objects.get(name='NXB Văn Học')
    pub_tongiao = Publisher.objects.get(name='NXB Tôn Giáo')
    
    books_data = [
        # === Tâm linh & Triết học ===
        {
            'title': 'Trong Sáng Như Pha Lê (In the Buddha\'s Words)',
            'slug': 'trong-sang-nhu-pha-le',
            'description': 'Đây là "bản đồ" hệ thống nhất cho người muốn đọc Kinh tạng Pāli mà không bị lạc giữa khối lượng đồ sộ của các bộ Nikaya.',
            'price': Decimal('185000'),
            'original_price': Decimal('220000'),
            'stock_quantity': 50,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Bhikkhu Bodhi',
            'is_featured': True,
        },
        {
            'title': 'Đức Phật Đã Dạy Những Gì (What the Buddha Taught)',
            'slug': 'duc-phat-da-day-nhung-gi',
            'description': 'Một cuốn sách kinh điển, giải thích súc tích các khái niệm Tứ Diệu Đế, Vô Ngã theo đúng tinh thần Theravada.',
            'price': Decimal('95000'),
            'original_price': Decimal('120000'),
            'stock_quantity': 80,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Walpola Rahula',
            'is_featured': True,
        },
        {
            'title': 'Khi Nào Chim Sắt Bay',
            'slug': 'khi-nao-chim-sat-bay',
            'description': 'Cung cấp cái nhìn rất sâu về bản chất tâm, bổ trợ cho khái niệm "Vạn pháp duy tâm tạo".',
            'price': Decimal('145000'),
            'stock_quantity': 35,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Tulku Urgyen Rinpoche',
        },
        {
            'title': 'Thiền Giữa Đời Thường',
            'slug': 'thien-giua-doi-thuong',
            'description': 'Tập trung vào chánh niệm trong mọi hoạt động, rất hợp với lối sống sinh viên bận rộn.',
            'price': Decimal('125000'),
            'stock_quantity': 60,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Sayadaw U Tejaniya',
        },
        {
            'title': 'Cổ Học Tinh Hoa',
            'slug': 'co-hoc-tinh-hoa',
            'description': 'Những bài học đạo đức, triết lý phương Đông cô đọng, giúp rèn luyện tâm tính.',
            'price': Decimal('89000'),
            'original_price': Decimal('110000'),
            'stock_quantity': 100,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_trithuc,
            'author_name': 'Nguyễn Hiến Lê',
            'is_featured': True,
        },
        {
            'title': 'Sự Im Lặng Của Thánh Nhân',
            'slug': 'su-im-lang-cua-thanh-nhan',
            'description': 'Phân tích về những vấn đề siêu hình mà Đức Phật giữ im lặng, giúp hiểu rõ hơn về tính thực tiễn của đạo Phật.',
            'price': Decimal('135000'),
            'stock_quantity': 45,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Thích Nhất Hạnh',
        },
        {
            'title': 'Sống Trong Tự Do',
            'slug': 'song-trong-tu-do',
            'description': 'Tuyển tập các bài pháp thoại đầy trí tuệ và sự hài hước của vị thiền sư nổi tiếng hệ phái Forest Tradition.',
            'price': Decimal('155000'),
            'stock_quantity': 40,
            'category': cat_tamlinh,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tongiao,
            'author_name': 'Ajahn Chah',
        },
        
        # === Phát triển bản thân ===
        {
            'title': 'Lối Sống Tối Giản Thời Công Nghệ (Digital Minimalism)',
            'slug': 'loi-song-toi-gian-thoi-cong-nghe',
            'description': 'Giúp bạn kiểm soát sự xao nhãng từ mạng xã hội để tập trung vào công việc.',
            'price': Decimal('169000'),
            'original_price': Decimal('199000'),
            'stock_quantity': 70,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_alpha,
            'author_name': 'Cal Newport',
            'is_featured': True,
        },
        {
            'title': 'Lối Sống Khắc Kỷ (The Daily Stoic)',
            'slug': 'loi-song-khac-ky',
            'description': 'Những bài học ngắn gọn mỗi ngày để giữ tâm bình thản trước áp lực deadline và thi cử.',
            'price': Decimal('179000'),
            'stock_quantity': 55,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_alpha,
            'author_name': 'Ryan Holiday',
            'is_featured': True,
        },
        {
            'title': 'Tư Duy Ngược (Reverse Thinking)',
            'slug': 'tu-duy-nguoc',
            'description': 'Giúp bạn phá vỡ những rào cản tư duy thông thường trong việc giải quyết vấn đề.',
            'price': Decimal('135000'),
            'stock_quantity': 40,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tre,
            'author_name': 'Nguyễn Anh Dũng',
        },
        {
            'title': 'Cứ Đi Tiếp Đi (Keep Going)',
            'slug': 'cu-di-tiep-di',
            'description': 'Một cuốn sách truyền cảm hứng cho những lúc bạn cảm thấy mệt mỏi với các dự án lập trình dài hơi.',
            'price': Decimal('115000'),
            'stock_quantity': 65,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_nhanam,
            'author_name': 'Austin Kleon',
        },
        {
            'title': 'Làm Chủ (Mastery)',
            'slug': 'lam-chu-mastery',
            'description': 'Phân tích lộ trình để trở thành bậc thầy trong một lĩnh vực, rất hợp cho người theo đuổi sự nghiệp IT.',
            'price': Decimal('225000'),
            'original_price': Decimal('280000'),
            'stock_quantity': 30,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_alpha,
            'author_name': 'Robert Greene',
        },
        {
            'title': 'Sao Chúng Ta Lại Ngủ (Why We Sleep)',
            'slug': 'sao-chung-ta-lai-ngu',
            'description': 'Hiểu về giấc ngủ để tối ưu hóa não bộ cho việc học ngôn ngữ và lập trình.',
            'price': Decimal('189000'),
            'stock_quantity': 45,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_alpha,
            'author_name': 'Matthew Walker',
        },
        {
            'title': 'Đỉnh Cao (Peak)',
            'slug': 'dinh-cao-peak',
            'description': 'Giải mã về "luyện tập có chủ đích", phương pháp nhanh nhất để giỏi bất cứ thứ gì.',
            'price': Decimal('175000'),
            'stock_quantity': 35,
            'category': cat_phattrien,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_alpha,
            'author_name': 'Anders Ericsson',
        },
        
        # === Văn học Việt Nam ===
        {
            'title': 'Vang Bóng Một Thời',
            'slug': 'vang-bong-mot-thoi',
            'description': 'Những nét đẹp văn hóa, thú ăn chơi thanh tao của người xưa, giúp bạn thư giãn sau những giờ học kỹ thuật khô khan.',
            'price': Decimal('85000'),
            'original_price': Decimal('99000'),
            'stock_quantity': 90,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_vanhoc,
            'author_name': 'Nguyễn Tuân',
            'is_featured': True,
        },
        {
            'title': 'Số Đỏ',
            'slug': 'so-do',
            'description': 'Để hiểu về sự trào phúng, sắc sảo và các vấn đề xã hội, giúp tư duy sắc bén hơn.',
            'price': Decimal('75000'),
            'stock_quantity': 120,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_vanhoc,
            'author_name': 'Vũ Trọng Phụng',
        },
        {
            'title': 'Cho Tôi Xin Một Vé Đi Tuổi Thơ',
            'slug': 'cho-toi-xin-mot-ve-di-tuoi-tho',
            'description': 'Một chút khoảng lặng tâm hồn, giúp cân bằng lại sự căng thẳng của việc học tập.',
            'price': Decimal('68000'),
            'stock_quantity': 150,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tre,
            'author_name': 'Nguyễn Nhật Ánh',
            'is_featured': True,
        },
        {
            'title': 'Nỗi Buồn Chiến Tranh',
            'slug': 'noi-buon-chien-tranh',
            'description': 'Một trong những tác phẩm quan trọng nhất của văn học hiện đại Việt Nam, đầy tính nhân văn và suy ngẫm.',
            'price': Decimal('95000'),
            'stock_quantity': 60,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_vanhoc,
            'author_name': 'Bảo Ninh',
        },
        {
            'title': 'Thương Nhớ Mười Hai',
            'slug': 'thuong-nho-muoi-hai',
            'description': 'Những dòng văn thấm đẫm tình yêu quê hương, đất nước và sự tinh tế trong cảm xúc.',
            'price': Decimal('89000'),
            'stock_quantity': 55,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_vanhoc,
            'author_name': 'Vũ Bằng',
        },
        {
            'title': 'Mắt Biếc',
            'slug': 'mat-biec',
            'description': 'Một câu chuyện đẹp về sự thuần khiết và kiên định, mang lại những góc nhìn nhẹ nhàng về tình cảm con người.',
            'price': Decimal('78000'),
            'original_price': Decimal('95000'),
            'stock_quantity': 200,
            'category': cat_vanhoc,
            'language': lang_vi,
            'book_format': fmt_paperback,
            'publisher': pub_tre,
            'author_name': 'Nguyễn Nhật Ánh',
            'is_featured': True,
        },
    ]
    
    for book_data in books_data:
        author_name = book_data.pop('author_name')
        author = Author.objects.get(name=author_name)
        
        book, created = Book.objects.get_or_create(
            slug=book_data['slug'],
            defaults={**book_data, 'is_active': True}
        )
        if created:
            book.authors.add(author)
            # Create book detail
            BookDetail.objects.get_or_create(
                book=book,
                defaults={'pages': 250, 'weight': Decimal('300')}
            )
    
    print(f"  Created {len(books_data)} books")

def seed_tags():
    """Create tags"""
    print("Creating tags...")
    tags = [
        'bestseller', 'phat-giao', 'thien-dinh', 'tu-duy', 'nang-suat',
        'van-hoc-viet', 'co-dien', 'hien-dai', 'tam-ly', 'triet-hoc',
        'self-help', 'kinh-dien', 'sach-hay'
    ]
    for tag_name in tags:
        Tag.objects.get_or_create(name=tag_name, defaults={'slug': tag_name})
    print(f"  Created {len(tags)} tags")

def seed_customers():
    """Create sample customers"""
    print("Creating customers...")
    bronze = MemberTier.objects.get(name='bronze')
    silver = MemberTier.objects.get(name='silver')
    gold = MemberTier.objects.get(name='gold')
    
    customers_data = [
        {'name': 'Nguyễn Văn An', 'email': 'an.nguyen@gmail.com', 'phone': '0901234567', 'member_tier': gold, 'loyalty_points': 5500},
        {'name': 'Trần Thị Bình', 'email': 'binh.tran@gmail.com', 'phone': '0912345678', 'member_tier': silver, 'loyalty_points': 2000},
        {'name': 'Lê Văn Cường', 'email': 'cuong.le@gmail.com', 'phone': '0923456789', 'member_tier': bronze, 'loyalty_points': 500},
        {'name': 'Phạm Thị Dung', 'email': 'dung.pham@gmail.com', 'phone': '0934567890', 'member_tier': silver, 'loyalty_points': 1500},
        {'name': 'Hoàng Văn Em', 'email': 'em.hoang@gmail.com', 'phone': '0945678901', 'member_tier': bronze, 'loyalty_points': 100},
    ]
    
    for cust in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=cust['email'],
            defaults=cust
        )
        if created:
            # Create address
            Address.objects.create(
                customer=customer,
                full_name=cust['name'],
                phone=cust['phone'],
                street_address='123 Đường ABC',
                city='TP. Hồ Chí Minh',
                state='Quận 1',
                postal_code='70000',
                country='Vietnam',
                is_default=True
            )
    print(f"  Created {len(customers_data)} customers")

def seed_staff():
    """Create sample staff"""
    print("Creating staff...")
    staff_data = [
        {'name': 'Nguyễn Quản Lý', 'email': 'manager@bookstore.com', 'employee_id': 'EMP001'},
        {'name': 'Trần Nhân Viên', 'email': 'staff1@bookstore.com', 'employee_id': 'EMP002'},
        {'name': 'Lê Kho Hàng', 'email': 'warehouse@bookstore.com', 'employee_id': 'EMP003'},
    ]
    for staff in staff_data:
        Staff.objects.get_or_create(employee_id=staff['employee_id'], defaults=staff)
    print(f"  Created {len(staff_data)} staff members")

def seed_suppliers():
    """Create suppliers"""
    print("Creating suppliers...")
    suppliers_data = [
        {'name': 'Nhà Phân Phối Miền Bắc', 'code': 'SUP001', 'contact_person': 'Nguyễn Văn A', 'email': 'supplier1@email.com', 'phone': '0241234567'},
        {'name': 'Nhà Phân Phối Miền Nam', 'code': 'SUP002', 'contact_person': 'Trần Văn B', 'email': 'supplier2@email.com', 'phone': '0281234567'},
        {'name': 'Công ty Sách Quốc Tế', 'code': 'SUP003', 'contact_person': 'John Smith', 'email': 'supplier3@email.com', 'phone': '0291234567'},
    ]
    for sup in suppliers_data:
        Supplier.objects.get_or_create(code=sup['code'], defaults=sup)
    print(f"  Created {len(suppliers_data)} suppliers")

def seed_warehouses():
    """Create warehouses"""
    print("Creating warehouses...")
    warehouses_data = [
        {'name': 'Kho Hà Nội', 'code': 'WH001', 'address': '100 Đường Láng, Đống Đa', 'city': 'Hà Nội', 'capacity': 10000, 'is_primary': True},
        {'name': 'Kho TP.HCM', 'code': 'WH002', 'address': '200 Nguyễn Văn Linh, Quận 7', 'city': 'TP. Hồ Chí Minh', 'capacity': 15000},
        {'name': 'Kho Đà Nẵng', 'code': 'WH003', 'address': '50 Trần Phú', 'city': 'Đà Nẵng', 'capacity': 5000},
    ]
    for wh in warehouses_data:
        Warehouse.objects.get_or_create(code=wh['code'], defaults=wh)
    print(f"  Created {len(warehouses_data)} warehouses")

def seed_inventory():
    """Create inventory records"""
    print("Creating inventory records...")
    warehouse = Warehouse.objects.get(code='WH001')
    books = Book.objects.all()
    
    for book in books:
        Inventory.objects.get_or_create(
            book=book,
            warehouse=warehouse,
            defaults={
                'quantity': book.stock_quantity,
                'min_stock_level': 10,
                'reorder_point': 20
            }
        )
    print(f"  Created inventory records for {books.count()} books")

def seed_payment_methods():
    """Create payment methods"""
    print("Creating payment methods...")
    methods = [
        {'name': 'cod', 'display_name': 'Thanh toán khi nhận hàng (COD)', 'is_active': True},
        {'name': 'bank_transfer', 'display_name': 'Chuyển khoản ngân hàng', 'is_active': True},
        {'name': 'momo', 'display_name': 'Ví MoMo', 'is_active': True},
        {'name': 'zalopay', 'display_name': 'ZaloPay', 'is_active': True},
        {'name': 'vnpay', 'display_name': 'VNPay', 'is_active': True},
        {'name': 'credit_card', 'display_name': 'Thẻ tín dụng/Ghi nợ', 'is_active': True},
    ]
    for method in methods:
        PaymentMethod.objects.get_or_create(name=method['name'], defaults=method)
    print(f"  Created {len(methods)} payment methods")

def seed_shipping_methods():
    """Create shipping methods"""
    print("Creating shipping methods...")
    methods = [
        {'name': 'Giao hàng tiêu chuẩn', 'code': 'STANDARD', 'base_cost': Decimal('30000'), 'estimated_days_min': 3, 'estimated_days_max': 5},
        {'name': 'Giao hàng nhanh', 'code': 'EXPRESS', 'base_cost': Decimal('50000'), 'estimated_days_min': 1, 'estimated_days_max': 2},
        {'name': 'Giao hàng hỏa tốc', 'code': 'SAME_DAY', 'base_cost': Decimal('80000'), 'estimated_days_min': 0, 'estimated_days_max': 1},
    ]
    for method in methods:
        ShippingMethod.objects.get_or_create(code=method['code'], defaults=method)
    print(f"  Created {len(methods)} shipping methods")

def seed_coupons():
    """Create coupons"""
    print("Creating coupons...")
    coupons = [
        {
            'code': 'WELCOME10',
            'description': 'Giảm 10% cho khách hàng mới',
            'coupon_type': 'percentage',
            'discount_value': Decimal('10'),
            'min_purchase_amount': Decimal('100000'),
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(days=365),
            'usage_limit': 1000,
        },
        {
            'code': 'FREESHIP',
            'description': 'Miễn phí vận chuyển đơn từ 200k',
            'coupon_type': 'fixed',
            'discount_value': Decimal('30000'),
            'min_purchase_amount': Decimal('200000'),
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(days=30),
            'usage_limit': 500,
        },
        {
            'code': 'LUNAR2026',
            'description': 'Giảm 20% mừng Tết Nguyên Đán',
            'coupon_type': 'percentage',
            'discount_value': Decimal('20'),
            'max_discount_amount': Decimal('100000'),
            'min_purchase_amount': Decimal('300000'),
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(days=60),
            'usage_limit': 200,
        },
    ]
    for coupon in coupons:
        Coupon.objects.get_or_create(code=coupon['code'], defaults=coupon)
    print(f"  Created {len(coupons)} coupons")

def seed_system_config():
    """Create system configurations"""
    print("Creating system configs...")
    configs = [
        {'key': 'site_name', 'value': 'Bookstore Assign3', 'value_type': 'string', 'is_public': True},
        {'key': 'currency', 'value': 'VND', 'value_type': 'string', 'is_public': True},
        {'key': 'tax_rate', 'value': '10', 'value_type': 'decimal', 'is_public': False},
        {'key': 'free_shipping_threshold', 'value': '500000', 'value_type': 'integer', 'is_public': True},
        {'key': 'contact_email', 'value': 'contact@bookstore.com', 'value_type': 'string', 'is_public': True},
        {'key': 'contact_phone', 'value': '1900 1234', 'value_type': 'string', 'is_public': True},
    ]
    for config in configs:
        SystemConfig.objects.get_or_create(key=config['key'], defaults=config)
    print(f"  Created {len(configs)} system configs")

def run_seed():
    """Run all seed functions"""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)
    
    seed_member_tiers()
    seed_languages()
    seed_book_formats()
    seed_categories()
    seed_authors()
    seed_publishers()
    seed_tags()
    seed_books()
    seed_customers()
    seed_staff()
    seed_suppliers()
    seed_warehouses()
    seed_inventory()
    seed_payment_methods()
    seed_shipping_methods()
    seed_coupons()
    seed_system_config()
    
    print("=" * 50)
    print("Database seeding completed successfully!")
    print("=" * 50)
    
    # Summary
    print("\nSummary:")
    print(f"  - Books: {Book.objects.count()}")
    print(f"  - Authors: {Author.objects.count()}")
    print(f"  - Categories: {Category.objects.count()}")
    print(f"  - Customers: {Customer.objects.count()}")
    print(f"  - Staff: {Staff.objects.count()}")
    print(f"  - Publishers: {Publisher.objects.count()}")
    print(f"  - Warehouses: {Warehouse.objects.count()}")
    print(f"  - Payment Methods: {PaymentMethod.objects.count()}")
    print(f"  - Shipping Methods: {ShippingMethod.objects.count()}")
    print(f"  - Coupons: {Coupon.objects.count()}")


if __name__ == '__main__':
    run_seed()
