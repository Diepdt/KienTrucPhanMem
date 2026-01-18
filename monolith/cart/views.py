from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from books.models import Book
from accounts.models import Customer

def add_to_cart(request, book_id):
    # 1. Kiểm tra đăng nhập (lấy ID từ session)
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login') # Chưa đăng nhập thì bắt đăng nhập

    # 2. Lấy đối tượng Customer và Book
    customer = Customer.objects.get(id=customer_id)
    book = get_object_or_404(Book, id=book_id)

    # 3. Lấy hoặc tạo giỏ hàng cho khách (Logic Monolithic)
    cart, created = Cart.objects.get_or_create(customer=customer)

    # 4. Thêm sách vào CartItem (Logic tương tự slide trang 16) [cite: 346]
    # Kiểm tra xem sách đã có trong giỏ chưa để tăng số lượng
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1 # Mặc định là 1 theo slide [cite: 350]
        cart_item.save()

    return redirect('cart_detail')

def cart_detail(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    # Lấy giỏ hàng hiển thị
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        items = []
    
    return render(request, 'cart/cart_detail.html', {'items': items})