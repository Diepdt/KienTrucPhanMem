from django.urls import path
from store.controllers.staffController import views

app_name = 'staff'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:book_id>/stock/', views.stock_update, name='stock_update'),
    path('books/import/', views.book_import, name='book_import'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
