from django.urls import path
from . import views

app_name = 'clean'

urlpatterns = [
    path('books/', views.book_list_view, name='book_list'),
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<int:book_id>/', views.update_cart_quantity_view, name='update_cart_quantity'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
