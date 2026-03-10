# micro/book_service/books/views.py
"""
Views cho Book Service - Quản lý sách và Frontend chính
"""
from django.shortcuts import render
from django.http import JsonResponse
from .models import Book

# URLs của các Service khác
CUSTOMER_SERVICE_URL = "http://127.0.0.1:8001"
CART_SERVICE_URL = "http://127.0.0.1:8003"


# ==================== API ENDPOINTS ====================
# Các endpoint này được các Service khác gọi

def get_book_api(request, book_id):
    """
    API: Lấy thông tin chi tiết của một cuốn sách.
    Được Cart Service gọi để kiểm tra tồn kho và lấy giá.
    """
    try:
        book = Book.objects.get(id=book_id)
        return JsonResponse({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'price': float(book.price),
            'stock': book.stock
        })
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)


def get_all_books_api(request):
    """
    API: Lấy danh sách tất cả sách.
    """
    books = Book.objects.all()
    data = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': float(book.price),
        'stock': book.stock
    } for book in books]
    return JsonResponse({'books': data})


# ==================== UI VIEWS ====================
# Các view này render HTML cho người dùng

def book_list_ui(request):
    """
    UI: Trang danh sách sách (Homepage).
    Book Service đóng vai trò Frontend chính.
    """
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {
        'books': books,
        'cart_service_url': CART_SERVICE_URL,
        'customer_service_url': CUSTOMER_SERVICE_URL
    })


def login_page(request):
    """
    UI: Trang đăng nhập.
    Form sẽ gọi API đến Customer Service qua JavaScript.
    """
    return render(request, 'books/login.html', {
        'customer_service_url': CUSTOMER_SERVICE_URL
    })


def register_page(request):
    """
    UI: Trang đăng ký.
    Form sẽ gọi API đến Customer Service qua JavaScript.
    """
    return render(request, 'books/register.html', {
        'customer_service_url': CUSTOMER_SERVICE_URL
    })


def cart_page(request):
    """
    UI: Trang giỏ hàng.
    Sẽ gọi API đến Cart Service để lấy thông tin giỏ hàng.
    """
    return render(request, 'books/cart.html', {
        'cart_service_url': CART_SERVICE_URL
    })