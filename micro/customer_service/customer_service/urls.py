# micro/customer_service/customer_service/urls.py
"""
URL configuration for customer_service project.
Service chạy trên port 8001
"""
from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # API Endpoints - Được gọi từ Frontend ở Book Service
    path('api/register/', views.register_api, name='register'),
    path('api/login/', views.login_api, name='login'),
    path('api/customers/<int:customer_id>/', views.get_customer_api, name='get_customer'),
]