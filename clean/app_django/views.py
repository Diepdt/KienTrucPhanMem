from django.shortcuts import render, redirect
from django.http import JsonResponse
import sys
import os
from pathlib import Path

from clean.core.usecases.cart_usecases import (
    AddBookToCartUseCase, ListBooksUseCase, LoginUseCase,
    GetCartUseCase, RemoveFromCartUseCase, UpdateCartQuantityUseCase
)
from clean.infrastructure.repositories import (
    DjangoCustomerRepository, DjangoBookRepository, DjangoCartRepository
)
from clean.core.usecases.cart_usecases import (
    AddBookToCartUseCase, ListBooksUseCase, LoginUseCase, RegisterUseCase, # <--- Thêm
    GetCartUseCase, RemoveFromCartUseCase, UpdateCartQuantityUseCase
)

customer_repo = DjangoCustomerRepository()
book_repo = DjangoBookRepository()
cart_repo = DjangoCartRepository()

def book_list_view(request):
    """View: Danh sách sách"""
    list_books_usecase = ListBooksUseCase(book_repo)
    books = list_books_usecase.execute()
    return render(request, 'clean/books/book_list.html', {'books': books})

def add_to_cart_view(request, book_id):
    """View: Thêm vào giỏ hàng"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({"success": False, "error": "Vui lòng đăng nhập"}, status=401)
    
    add_to_cart_usecase = AddBookToCartUseCase(cart_repo, book_repo, customer_repo)
    result = add_to_cart_usecase.execute(customer_id, book_id)
    
    return JsonResponse(result, status=200 if result['success'] else 400)

def cart_detail_view(request):
    """View: Chi tiết giỏ hàng"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('clean:login')
    
    get_cart_usecase = GetCartUseCase(cart_repo)
    result = get_cart_usecase.execute(customer_id)
    
    if not result['success']:
        return render(request, 'clean/cart/cart_detail.html', {'items': [], 'total_price': 0})
    
    cart = result['cart']
    return render(request, 'clean/cart/cart_detail.html', {'items': cart.items, 'total_price': cart.get_total_price()})

def remove_from_cart_view(request, book_id):
    """View: Xóa khỏi giỏ"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('clean:login')
    
    remove_usecase = RemoveFromCartUseCase(cart_repo)
    remove_usecase.execute(customer_id, book_id)
    return redirect('clean:cart_detail')

def update_cart_quantity_view(request, book_id):
    """View: Cập nhật số lượng"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('clean:login')
    
    action = request.GET.get('action')
    cart = cart_repo.get_by_customer(customer_id)
    
    if not cart:
        return redirect('clean:cart_detail')
    
    new_qty = 0
    for item in cart.items:
        if item.book_id == book_id:
            new_qty = item.quantity + 1 if action == 'increase' else max(0, item.quantity - 1)
            break
    
    update_usecase = UpdateCartQuantityUseCase(cart_repo)
    update_usecase.execute(customer_id, book_id, new_qty)
    return redirect('clean:cart_detail')

def login_view(request):
    """View: Đăng nhập"""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        login_usecase = LoginUseCase(customer_repo)
        result = login_usecase.execute(email, password)
        
        if result['success']:
            customer = result['customer']
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name
            return redirect('clean:book_list')
        else:
            return render(request, 'clean/accounts/login.html', {'error': result['error']})
    
    return render(request, 'clean/accounts/login.html')

def logout_view(request):
    """View: Đăng xuất"""
    request.session.flush()
    return redirect('clean:login')

def register_view(request):
    """View: Đăng ký"""
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        register_usecase = RegisterUseCase(customer_repo)
        result = register_usecase.execute(name, email, password)
        
        if result['success']:
            return redirect('clean:login')
        else:
            return render(request, 'clean/accounts/register.html', {'error': result['error']})
    
    return render(request, 'clean/accounts/register.html')