from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LaptopViewSet, LaptopDetailPublicView, UpdateStockView

router = DefaultRouter()
router.register(r'laptops', LaptopViewSet, basename='laptop')

urlpatterns = [
    path('laptops/update-stock/', UpdateStockView.as_view(), name='update-stock'),
    path('laptops/<int:pk>/detail/', LaptopDetailPublicView.as_view(), name='laptop-detail-public'),
    path('', include(router.urls)),
]
