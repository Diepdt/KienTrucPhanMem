from django.urls import path
from store.controllers.orderController import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:book_id>/', views.cart_add, name='add'),
    path('update/<int:item_id>/', views.cart_update, name='update'),
    path('remove/<int:item_id>/', views.cart_remove, name='remove'),
    path('clear/', views.cart_clear, name='clear'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.checkout_process, name='checkout_process'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
]
