from django.urls import path
from .views import PaymentMethodListView, PaymentMethodDetailView, CreatePaymentView, PaymentByOrderView

urlpatterns = [
    path('payment/methods/', PaymentMethodListView.as_view(), name='payment-methods'),
    path('payment/methods/<int:pk>/', PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    path('payment/create/', CreatePaymentView.as_view(), name='create-payment'),
    path('payment/order/<int:order_id>/', PaymentByOrderView.as_view(), name='payment-by-order'),
]
