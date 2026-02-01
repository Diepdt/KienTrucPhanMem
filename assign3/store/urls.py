from django.urls import path, include

# Không dùng app_name ở đây vì các controller đã có app_name riêng

urlpatterns = [
    path('books/', include('store.controllers.bookController.urls')),
    path('customer/', include('store.controllers.customerController.urls')),
    path('staff/', include('store.controllers.staffController.urls')),
    path('cart/', include('store.controllers.orderController.urls')),
]
