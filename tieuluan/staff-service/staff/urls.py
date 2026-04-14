from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, StaffLoginView, StaffLogoutView, VerifyTokenView

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, basename='staff')

urlpatterns = [
    path('', include(router.urls)),
    path('staff/login/', StaffLoginView.as_view(), name='staff-login'),
    path('staff/logout/', StaffLogoutView.as_view(), name='staff-logout'),
    path('staff/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
]
