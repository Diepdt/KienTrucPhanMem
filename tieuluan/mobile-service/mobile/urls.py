from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MobileViewSet, MobileDetailPublicView, UpdateStockView

router = DefaultRouter()
router.register(r'mobiles', MobileViewSet, basename='mobile')

urlpatterns = [
    path('mobiles/update-stock/', UpdateStockView.as_view(), name='update-stock'),
    path('mobiles/<int:pk>/detail/', MobileDetailPublicView.as_view(), name='mobile-detail-public'),
    path('', include(router.urls)),
]
