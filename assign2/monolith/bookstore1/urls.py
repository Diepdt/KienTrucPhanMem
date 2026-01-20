from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Domain Package MVC Architecture URLs
    path('', lambda request: redirect('book:list')),  # Redirect home to book list
    path('', include('store.urls')),  # Include all store URLs
    
    # Legacy URLs (commented out - can be removed after migration)
    # path('', include('books.urls')),
    # path('auth/', include('accounts.urls')),
    # path('cart/', include('cart.urls')),
]