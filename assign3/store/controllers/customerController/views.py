from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from store.models import Customer, Order


def register(request):
    """
    Handle customer registration.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if Customer.objects.filter(email=email).exists():
            errors.append('Email already registered')
        
        if errors:
            return render(request, 'customer/register.html', {
                'errors': errors,
                'name': name,
                'email': email,
            })
        
        # Create customer (password will be hashed in model's save method)
        customer = Customer.objects.create(
            name=name,
            email=email,
            password=password
        )
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('customer:login')
    
    return render(request, 'customer/register.html')


def login(request):
    """
    Handle customer login.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        try:
            customer = Customer.objects.get(email=email)
            if customer.verify_password(password):
                # Set session
                request.session['customer_id'] = customer.id
                request.session['customer_name'] = customer.name
                request.session['is_customer'] = True
                
                messages.success(request, f'Welcome back, {customer.name}!')
                return redirect('book:list')
            else:
                messages.error(request, 'Invalid password')
        except Customer.DoesNotExist:
            messages.error(request, 'Email not found')
        
        return render(request, 'customer/login.html', {'email': email})
    
    return render(request, 'customer/login.html')


def logout(request):
    """
    Handle customer logout.
    """
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('customer:login')


def profile(request):
    """
    Display and edit customer profile.
    """
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Check if email is taken by another customer
        if email != customer.email and Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
        else:
            customer.name = name
            customer.email = email
            customer.save()
            request.session['customer_name'] = name
            messages.success(request, 'Profile updated successfully')
        
        return redirect('customer:profile')
    
    context = {
        'customer': customer,
    }
    return render(request, 'customer/profile.html', context)


def order_history(request):
    """
    Display customer's order history.
    """
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')
    
    orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'customer/order_history.html', context)


def order_detail(request, order_id):
    """
    Display details of a specific order.
    """
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')
    
    order = get_object_or_404(Order, id=order_id, customer_id=customer_id)
    
    context = {
        'order': order,
    }
    return render(request, 'customer/order_detail.html', context)
