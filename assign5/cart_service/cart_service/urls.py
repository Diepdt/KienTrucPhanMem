# micro/cart_service/cart_service/urls.py
"""
URL configuration for cart_service project.
Service chạy trên port 8003
"""
from django.contrib import admin
from django.urls import path
from cart import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # API Endpoints - Được gọi từ Frontend ở Book Service
    path('api/cart/add/', views.add_to_cart_api, name='add_to_cart'),
    path('api/cart/<int:customer_id>/', views.get_cart_api, name='get_cart'),
    path('api/cart/update/', views.update_cart_item_api, name='update_cart'),
    path('api/cart/remove/', views.remove_from_cart_api, name='remove_from_cart'),
]
