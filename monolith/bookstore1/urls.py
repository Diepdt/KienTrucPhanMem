from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),
    path('cart/', include('cart.urls')), # <--- Thêm dòng này
]