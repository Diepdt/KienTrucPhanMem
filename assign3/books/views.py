from django.shortcuts import render
from .models import Book

def book_list(request):
    # Lấy tất cả sách từ Database
    books = Book.objects.all()
    # Đẩy dữ liệu sang file HTML (template)
    return render(request, 'books/book_list.html', {'books': books})