from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem
from books.models import Book
from accounts.models import Customer

def add_to_cart(request, book_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập'}, status=401)
        return redirect('login')

    try:
        customer = Customer.objects.get(id=customer_id)
        book = get_object_or_404(Book, id=book_id)
        
        cart, created = Cart.objects.get_or_create(customer=customer)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()
        
        # Tính tổng số lượng trong giỏ hàng
        total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Đã thêm "{book.title}" vào giỏ hàng!',
                'cart_count': total_items
            })
    except Customer.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập'}, status=401)
        return redirect('login')

    return redirect('book_list')

def cart_detail(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        items = CartItem.objects.filter(cart=cart).select_related('book')
        total_price = sum(float(item.book.price) * item.quantity for item in items)
    except Cart.DoesNotExist:
        items = []
        total_price = 0
    
    return render(request, 'cart/cart_detail.html', {
        'items': items,
        'total_price': total_price
    })

def update_cart_item(request, item_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        cart_item = CartItem.objects.get(id=item_id)
        action = request.GET.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart_detail')