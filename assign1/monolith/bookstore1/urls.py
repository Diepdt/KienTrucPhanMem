from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),      # Trang chủ là list sách
    path('auth/', include('accounts.urls')), # Các link đăng nhập/ký
    path('cart/', include('cart.urls')),     # Các link giỏ hàng
]