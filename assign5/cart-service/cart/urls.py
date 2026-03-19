from django.urls import path
from .views import (CreateCartView, GetCartView, AddToCartView,
                    UpdateCartItemView, RemoveFromCartView,
                    ClearCartView, GetCartByCustomerInternalView,
                    AddToCartInternalView)

urlpatterns = [
    path('carts/create/', CreateCartView.as_view(), name='cart-create'),
    path('carts/<int:customer_id>/', GetCartView.as_view(), name='cart-get'),
    path('carts/<int:customer_id>/internal/', GetCartByCustomerInternalView.as_view(), name='cart-internal'),
    path('carts/<int:customer_id>/clear/', ClearCartView.as_view(), name='cart-clear'),
    path('carts/add/', AddToCartView.as_view(), name='cart-add'),
    path('carts/add-internal/', AddToCartInternalView.as_view(), name='cart-add-internal'),
    path('carts/items/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-item-update'),
    path('carts/items/<int:item_id>/remove/', RemoveFromCartView.as_view(), name='cart-item-remove'),
]
