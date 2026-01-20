# micro/book_service/book_service/urls.py
"""
URL configuration for book_service project.
Service chạy trên port 8002
"""
from django.contrib import admin
from django.urls import path
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # UI View - Trang danh sách sách cho người dùng
    path('', views.book_list_ui, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('cart/', views.cart_page, name='cart'),
    # API Endpoint - Cho các service khác gọi
    path('api/books/<int:book_id>/', views.get_book_api, name='get_book_api'),
    path('api/books/', views.get_all_books_api, name='get_all_books_api'),
]