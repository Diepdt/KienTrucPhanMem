from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookDetailPublicView, UpdateStockView

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('books/update-stock/', UpdateStockView.as_view(), name='update-stock'),
    path('books/<int:pk>/detail/', BookDetailPublicView.as_view(), name='book-detail-public'),
    path('', include(router.urls)),
]
