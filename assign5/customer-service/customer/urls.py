from django.urls import path
from .views import (RegisterView, LoginView, LogoutView,
                    CustomerDetailView, VerifyTokenView, CustomerListView)

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/register/', RegisterView.as_view(), name='register'),
    path('customers/login/', LoginView.as_view(), name='login'),
    path('customers/logout/', LogoutView.as_view(), name='logout'),
    path('customers/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('customers/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),
]
