from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal
from store.models import (
    Book, Customer, Cart, CartItem, 
    Order, OrderItem, Shipping, Payment
)


def get_or_create_cart(request):
    """
    Get or create a cart for the current user/session.
    """
    customer_id = request.session.get('customer_id')
    
    if customer_id:
        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id,
            defaults={'session_key': request.session.session_key}
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            customer__isnull=True
        )
    
    return cart


def cart_detail(request):
    """
    Display shopping cart contents.
    """
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'items': cart.items.select_related('book').all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }
    return render(request, 'cart/cart_detail.html', context)


def cart_add(request, book_id):
    """
    Add a book to the shopping cart.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if not book.is_in_stock():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Book is out of stock'}, status=400)
        messages.error(request, 'Sorry, this book is out of stock')
        return redirect('book:detail', book_id=book_id)
    
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if book already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Book already in cart, increase quantity
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added {book.title} to cart',
            'cart_total': cart.get_total_items(),
        })
    
    messages.success(request, f'Added "{book.title}" to cart')
    return redirect('cart:detail')


def cart_update(request, item_id):
    """
    Update quantity of a cart item.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')
        else:
            # Check stock availability
            if quantity > cart_item.book.stock_quantity:
                messages.error(request, f'Only {cart_item.book.stock_quantity} available in stock')
                quantity = cart_item.book.stock_quantity
            
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'total_price': str(cart.get_total_price()),
        })
    
    return redirect('cart:detail')


def cart_remove(request, item_id):
    """
    Remove an item from the shopping cart.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    book_title = cart_item.book.title
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Removed {book_title} from cart',
            'cart_total': cart.get_total_items(),
        })
    
    messages.success(request, f'Removed "{book_title}" from cart')
    return redirect('cart:detail')


def cart_clear(request):
    """
    Clear all items from the shopping cart.
    """
    cart = get_or_create_cart(request)
    cart.clear()
    
    messages.success(request, 'Cart has been cleared')
    return redirect('cart:detail')


def checkout(request):
    """
    Display checkout page with shipping and payment options.
    """
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.info(request, 'Please login to checkout')
        return redirect('customer:login')
    
    cart = get_or_create_cart(request)
    
    if cart.get_total_items() == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:detail')
    
    context = {
        'cart': cart,
        'items': cart.items.select_related('book').all(),
        'subtotal': cart.get_total_price(),
        'shipping_methods': Shipping.METHOD_CHOICES,
        'shipping_costs': Shipping.SHIPPING_COSTS,
        'payment_methods': Payment.METHOD_CHOICES,
    }
    return render(request, 'cart/checkout.html', context)


def checkout_process(request):
    """
    Process checkout and create order.
    """
    if request.method != 'POST':
        return redirect('cart:checkout')
    
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')
    
    cart = get_or_create_cart(request)
    
    if cart.get_total_items() == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:detail')
    
    # Get shipping info
    shipping_method = request.POST.get('shipping_method', 'standard')
    shipping_address = request.POST.get('address', '')
    shipping_city = request.POST.get('city', '')
    shipping_postal = request.POST.get('postal_code', '')
    shipping_country = request.POST.get('country', 'Vietnam')
    
    # Get payment info
    payment_method = request.POST.get('payment_method', 'credit_card')
    
    # Validate stock availability
    for item in cart.items.all():
        if item.quantity > item.book.stock_quantity:
            messages.error(request, f'Insufficient stock for "{item.book.title}"')
            return redirect('cart:checkout')
    
    # Create shipping record
    shipping = Shipping.objects.create(
        method=shipping_method,
        address=shipping_address,
        city=shipping_city,
        postal_code=shipping_postal,
        country=shipping_country
    )
    
    # Calculate total
    subtotal = cart.get_total_price()
    total = subtotal + shipping.cost
    
    # Create payment record
    payment = Payment.objects.create(
        method=payment_method,
        amount=total,
        status='pending'
    )
    
    # Create order
    order = Order.objects.create(
        customer_id=customer_id,
        shipping=shipping,
        payment=payment,
        total_amount=total,
        status='pending'
    )
    
    # Create order items and update stock
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            book=cart_item.book,
            quantity=cart_item.quantity,
            price=cart_item.book.price
        )
        # Reduce stock
        cart_item.book.reduce_stock(cart_item.quantity)
    
    # Clear the cart
    cart.clear()
    
    # Mark payment as completed (simplified)
    payment.mark_as_completed(transaction_id=f"TXN-{order.id}-{payment.id}")
    order.confirm()
    
    messages.success(request, f'Order #{order.id} placed successfully!')
    return redirect('cart:order_confirmation', order_id=order.id)


def order_confirmation(request, order_id):
    """
    Display order confirmation page.
    """
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')
    
    order = get_object_or_404(Order, id=order_id, customer_id=customer_id)
    
    context = {
        'order': order,
    }
    return render(request, 'cart/order_confirmation.html', context)
