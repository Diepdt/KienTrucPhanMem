from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from functools import wraps
from store.models import Staff, Book, Order


def staff_required(view_func):
    """
    Decorator to require staff login for a view.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('staff_id'):
            messages.error(request, 'Staff login required')
            return redirect('staff:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login(request):
    """
    Handle staff login.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        try:
            staff = Staff.objects.get(email=email)
            if staff.verify_password(password):
                # Set session
                request.session['staff_id'] = staff.id
                request.session['staff_name'] = staff.name
                request.session['staff_role'] = staff.role
                request.session['is_staff'] = True
                
                messages.success(request, f'Welcome, {staff.name}!')
                return redirect('staff:dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Staff.DoesNotExist:
            messages.error(request, 'Staff account not found')
        
        return render(request, 'staff/login.html', {'email': email})
    
    return render(request, 'staff/login.html')


def logout(request):
    """
    Handle staff logout.
    """
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('staff:login')


@staff_required
def dashboard(request):
    """
    Staff dashboard showing overview statistics.
    """
    stats = {
        'total_books': Book.objects.count(),
        'low_stock_books': Book.objects.filter(stock_quantity__lt=10).count(),
        'out_of_stock': Book.objects.filter(stock_quantity=0).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_orders': Order.objects.count(),
    }
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    low_stock_books = Book.objects.filter(stock_quantity__lt=10)[:5]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_books': low_stock_books,
    }
    return render(request, 'staff/dashboard.html', context)


@staff_required
def book_list(request):
    """
    List all books for inventory management.
    """
    books = Book.objects.all().order_by('title')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        books = books.filter(title__icontains=search) | books.filter(author__icontains=search)
    
    # Pagination
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'search': search,
    }
    return render(request, 'staff/book_list.html', context)


@staff_required
def book_add(request):
    """
    Add a new book to inventory.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        price = request.POST.get('price', '0')
        stock_quantity = request.POST.get('stock_quantity', '0')
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required')
        if not author:
            errors.append('Author is required')
        
        try:
            price = float(price)
            if price < 0:
                errors.append('Price must be positive')
        except ValueError:
            errors.append('Invalid price format')
        
        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                errors.append('Stock quantity must be non-negative')
        except ValueError:
            errors.append('Invalid stock quantity')
        
        if errors:
            return render(request, 'staff/book_form.html', {
                'errors': errors,
                'title': title,
                'author': author,
                'price': price,
                'stock_quantity': stock_quantity,
                'action': 'Add',
            })
        
        Book.objects.create(
            title=title,
            author=author,
            price=price,
            stock_quantity=stock_quantity
        )
        
        messages.success(request, f'Book "{title}" added successfully')
        return redirect('staff:book_list')
    
    return render(request, 'staff/book_form.html', {'action': 'Add'})


@staff_required
def book_edit(request, book_id):
    """
    Edit an existing book.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        price = request.POST.get('price', '0')
        stock_quantity = request.POST.get('stock_quantity', '0')
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required')
        if not author:
            errors.append('Author is required')
        
        try:
            price = float(price)
            if price < 0:
                errors.append('Price must be positive')
        except ValueError:
            errors.append('Invalid price format')
        
        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                errors.append('Stock quantity must be non-negative')
        except ValueError:
            errors.append('Invalid stock quantity')
        
        if errors:
            return render(request, 'staff/book_form.html', {
                'errors': errors,
                'book': book,
                'action': 'Edit',
            })
        
        book.title = title
        book.author = author
        book.price = price
        book.stock_quantity = stock_quantity
        book.save()
        
        messages.success(request, f'Book "{title}" updated successfully')
        return redirect('staff:book_list')
    
    return render(request, 'staff/book_form.html', {
        'book': book,
        'action': 'Edit',
    })


@staff_required
def book_delete(request, book_id):
    """
    Delete a book from inventory.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted successfully')
        return redirect('staff:book_list')
    
    return render(request, 'staff/book_confirm_delete.html', {'book': book})


@staff_required
def book_import(request):
    """
    Import books from CSV/JSON file.
    """
    if request.method == 'POST':
        import_file = request.FILES.get('file')
        
        if not import_file:
            messages.error(request, 'Please select a file to import')
            return redirect('staff:book_import')
        
        filename = import_file.name.lower()
        imported_count = 0
        errors = []
        
        try:
            if filename.endswith('.csv'):
                import csv
                import io
                
                decoded_file = import_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                
                for row in reader:
                    try:
                        Book.objects.create(
                            title=row.get('title', '').strip(),
                            author=row.get('author', '').strip(),
                            price=float(row.get('price', 0)),
                            stock_quantity=int(row.get('stock_quantity', row.get('stock', 0)))
                        )
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                        
            elif filename.endswith('.json'):
                import json
                
                data = json.loads(import_file.read().decode('utf-8'))
                books = data if isinstance(data, list) else data.get('books', [])
                
                for book_data in books:
                    try:
                        Book.objects.create(
                            title=book_data.get('title', '').strip(),
                            author=book_data.get('author', '').strip(),
                            price=float(book_data.get('price', 0)),
                            stock_quantity=int(book_data.get('stock_quantity', book_data.get('stock', 0)))
                        )
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Book error: {str(e)}")
            else:
                messages.error(request, 'Unsupported file format. Please use CSV or JSON.')
                return redirect('staff:book_import')
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} books')
            if errors:
                messages.warning(request, f'{len(errors)} errors occurred during import')
                
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
        
        return redirect('staff:book_list')
    
    return render(request, 'staff/book_import.html')


@staff_required
def stock_update(request, book_id):
    """
    Quick stock update for a book.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 0))
        
        if action == 'add':
            book.add_stock(quantity)
            messages.success(request, f'Added {quantity} to stock')
        elif action == 'set':
            book.stock_quantity = quantity
            book.save()
            messages.success(request, f'Stock set to {quantity}')
        
        return redirect('staff:book_list')
    
    return render(request, 'staff/stock_update.html', {'book': book})


@staff_required
def order_list(request):
    """
    List all orders for management.
    """
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'staff/order_list.html', context)


@staff_required
def order_detail(request, order_id):
    """
    View and manage order details.
    """
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        
        return redirect('staff:order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'staff/order_detail.html', context)
