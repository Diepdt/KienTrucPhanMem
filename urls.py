# FILE: bookstore1/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Trỏ tất cả đường dẫn gốc về file books/urls.py ở trên
    path('', include('books.urls')),
]