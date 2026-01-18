from django.shortcuts import render, redirect
from .models import Customer

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Kiểm tra user trong DB
            customer = Customer.objects.get(email=email, password=password)
            # Lưu ID vào session để đánh dấu đã đăng nhập
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name
            return redirect('book_list') # Quay về trang danh sách sách
        except Customer.DoesNotExist:
            return render(request, 'accounts/login.html', {'error': 'Sai thông tin'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    request.session.flush() # Xóa session
    return redirect('login')