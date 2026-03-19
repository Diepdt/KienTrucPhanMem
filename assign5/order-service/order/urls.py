from django.urls import path
from .views import CreateOrderView, OrderListView, OrderHistoryView, OrderDetailView, CustomerOrdersInternalView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/history/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/customer/<int:customer_id>/internal/', CustomerOrdersInternalView.as_view(), name='orders-internal'),
]
