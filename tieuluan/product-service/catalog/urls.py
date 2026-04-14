from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductInventoryUpdateView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('products/update-stock/', ProductInventoryUpdateView.as_view(), name='products-update-stock'),
    path('', include(router.urls)),
]
