from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal
from store.models import (
    Book, Customer, Cart, CartItem, 
    Order, OrderItem, ShippingMethod, Shipment, Payment, PaymentMethod, Address
)


def get_or_create_cart(request):
    """
    Get or create a cart for the current user/session.
    """
    customer_id = request.session.get('customer_id')
    
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        cart, created = Cart.objects.get_or_create(customer=customer)
    else:
        # For guest users, we'll use session-based cart lookup
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Store cart ID in session for guest users
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, customer__isnull=True)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    return cart


def cart_detail(request):
    """
    Display shopping cart contents.
    """
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'items': cart.items.select_related('book').all(),
        'total_price': cart.get_subtotal(),
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
    
    # Get customer's addresses
    customer = Customer.objects.get(id=customer_id)
    addresses = customer.addresses.all()
    
    # Get shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'cart': cart,
        'items': cart.items.select_related('book').all(),
        'subtotal': cart.get_subtotal(),
        'addresses': addresses,
        'shipping_methods': shipping_methods,
        'payment_methods': payment_methods,
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
    
    customer = Customer.objects.get(id=customer_id)
    
    # Get shipping info
    shipping_method_id = request.POST.get('shipping_method')
    shipping_address_id = request.POST.get('shipping_address')
    
    # Get payment info
    payment_method_id = request.POST.get('payment_method')
    
    # Handle new address if no existing address selected
    shipping_address = None
    if shipping_address_id:
        try:
            shipping_address = Address.objects.get(id=shipping_address_id)
        except Address.DoesNotExist:
            pass
    else:
        # Create new address from form
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        new_address = request.POST.get('new_address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        
        if full_name and phone and new_address and city:
            shipping_address = Address.objects.create(
                customer=customer,
                full_name=full_name,
                phone=phone,
                street_address=new_address,
                city=city,
                postal_code=postal_code,
                country='Vietnam',
                is_default=True
            )
    
    # Validate stock availability
    for item in cart.items.all():
        if item.quantity > item.book.stock_quantity:
            messages.error(request, f'Insufficient stock for "{item.book.title}"')
            return redirect('cart:checkout')
    
    # Get shipping method and calculate cost
    shipping_method = None
    shipping_cost = Decimal('30000')  # Default shipping cost
    if shipping_method_id:
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            shipping_cost = shipping_method.base_cost
        except ShippingMethod.DoesNotExist:
            pass
    
    # Calculate total
    subtotal = cart.get_subtotal()
    total = subtotal + shipping_cost
    
    # Generate order number
    import uuid
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    order = Order.objects.create(
        order_number=order_number,
        customer=customer,
        shipping_address=shipping_address,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        status='pending'
    )
    
    # Create order items and update stock
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            book=cart_item.book,
            quantity=cart_item.quantity,
            unit_price=cart_item.book.price
        )
        # Reduce stock
        cart_item.book.reduce_stock(cart_item.quantity)
    
    # Create payment record
    payment_method = None
    if payment_method_id:
        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
        except PaymentMethod.DoesNotExist:
            pass
    
    payment = Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=total,
        status='pending'
    )
    
    # Create shipment record
    if shipping_method:
        tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"
        Shipment.objects.create(
            order=order,
            shipping_method=shipping_method,
            tracking_number=tracking_number,
            shipping_cost=shipping_cost,
            status='pending'
        )
    
    # Clear the cart
    cart.clear()
    
    # Mark payment as completed (simplified for demo)
    payment.mark_as_completed()
    order.confirm()
    
    messages.success(request, f'Order #{order.order_number} placed successfully!')
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
