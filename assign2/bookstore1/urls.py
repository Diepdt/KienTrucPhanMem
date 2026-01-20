from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Domain Package MVC Architecture URLs
    path('', RedirectView.as_view(pattern_name='book:list', permanent=False)),
    path('', include('store.urls')),
]