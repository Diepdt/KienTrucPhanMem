from django.contrib import admin
from django.urls import path, include # Nhớ import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')), # Trang chủ sẽ hiện danh sách sách luôn
]