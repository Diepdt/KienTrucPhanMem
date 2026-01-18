from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Monolith URLs
    path('books/', include('monolith.books.urls')),
    path('cart/', include('monolith.cart.urls')),
    path('accounts/', include('monolith.accounts.urls')),
    # Clean Architecture URLs
    path('clean/', include('clean.app_django.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
