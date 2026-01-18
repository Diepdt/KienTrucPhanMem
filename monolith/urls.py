from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
]
