from django.contrib import admin
from django.urls import path, re_path
from gateway.views import ProxyView, HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    # Route tất cả request đến ProxyView
    re_path(r'^api/(?P<path>.*)$', ProxyView.as_view(), name='proxy'),
    path('', ProxyView.as_view(), {'path': ''}, name='root'),
]
