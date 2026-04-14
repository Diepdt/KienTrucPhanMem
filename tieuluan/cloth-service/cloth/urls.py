from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClothViewSet, ClothDetailPublicView, UpdateStockView

router = DefaultRouter()
router.register(r'clothes', ClothViewSet, basename='cloth')

urlpatterns = [
    path('clothes/update-stock/', UpdateStockView.as_view(), name='cloth-update-stock'),
    path('clothes/<int:pk>/detail/', ClothDetailPublicView.as_view(), name='cloth-detail-public'),
    path('', include(router.urls)),
]
