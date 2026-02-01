from django.urls import path
from store.controllers.bookController import views

app_name = 'book'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('<int:book_id>/', views.book_detail, name='detail'),
    path('search/', views.book_search, name='search'),
    path('<int:book_id>/rate/', views.rate_book, name='rate'),
]
