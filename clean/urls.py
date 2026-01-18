from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Dùng include để nạp URL của app_django, lúc này namespace='clean' mới có hiệu lực
    path('', include('clean.app_django.urls')), 
]