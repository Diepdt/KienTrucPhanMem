from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from books.models import Book
from accounts.models import Customer

def add_to_cart(request, book_id):
    # LẤY KHÁCH HÀNG (Hardcode ID=1 để test nhanh, sau này làm Login sẽ thay bằng session)
    # Lưu ý: Bạn phải tạo Customer ID=1 trong Admin trước nhé!
    customer = Customer.objects.get(id=1) 
    
    # Lấy sách
    book = get_object_or_404(Book, id=book_id)
    
    # Tìm hoặc tạo Giỏ hàng cho khách
    cart, created = Cart.objects.get_or_create(customer=customer)
    
    # Kiểm tra xem sách đã có trong giỏ chưa
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not created:
        # Nếu có rồi thì tăng số lượng
        cart_item.quantity += 1
        cart_item.save()
    
    # Quay lại trang danh sách sách
    return redirect('book_list')

def cart_detail(request):
    # Lấy giỏ hàng của khách ID=1
    try:
        customer = Customer.objects.get(id=1)
        cart = Cart.objects.get(customer=customer)
        items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        items = []
        cart = None

    return render(request, 'cart/cart_detail.html', {'items': items, 'cart': cart})