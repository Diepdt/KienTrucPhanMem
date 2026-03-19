from django.urls import path
from .views import (
    CreateOrderView,
    OrderListView,
    OrderHistoryView,
    OrderDetailView,
    CustomerOrdersInternalView,
    AdminOrderSummaryView,
    AdminOrderListView,
    AdminOrderDetailView,
)

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/history/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/admin-summary/', AdminOrderSummaryView.as_view(), name='order-admin-summary'),
    path('orders/admin/', AdminOrderListView.as_view(), name='order-admin-list'),
    path('orders/admin/<int:order_id>/', AdminOrderDetailView.as_view(), name='order-admin-detail'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/customer/<int:customer_id>/internal/', CustomerOrdersInternalView.as_view(), name='orders-internal'),
]
