from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('monolith.books.urls')),
    path('cart/', include('monolith.cart.urls')),
    path('accounts/', include('monolith.accounts.urls')),
]

# Serve static files trong DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
