from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, ManagerLoginView, VerifyTokenView, ManageStaffView

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')

urlpatterns = [
    path('', include(router.urls)),
    path('manager/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('manager/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('manager/staff/', ManageStaffView.as_view(), name='manage-staff'),
]
