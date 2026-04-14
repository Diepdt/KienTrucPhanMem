from django.urls import path
from .views import ShippingMethodListView, ShippingMethodDetailView, CreateShipmentView, ShipmentByOrderView

urlpatterns = [
    path('shipping/methods/', ShippingMethodListView.as_view(), name='shipping-methods'),
    path('shipping/methods/<int:pk>/', ShippingMethodDetailView.as_view(), name='shipping-method-detail'),
    path('shipping/create/', CreateShipmentView.as_view(), name='create-shipment'),
    path('shipping/order/<int:order_id>/', ShipmentByOrderView.as_view(), name='shipment-by-order'),
]
