from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from store.models import Book, CartItem, Rating


def book_list(request):
    """
    Display list of all books with search and filter capabilities.
    """
    books = Book.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Filter by author
    author_filter = request.GET.get('author', '')
    if author_filter:
        books = books.filter(author__icontains=author_filter)
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'title')
    if sort_by in ['title', '-title', 'price', '-price', 'author', '-author']:
        books = books.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(books, 12)  # 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'search_query': search_query,
        'author_filter': author_filter,
        'sort_by': sort_by,
    }
    return render(request, 'book/book_list.html', context)


def book_detail(request, book_id):
    """
    Display detailed information about a specific book.
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Get average rating
    avg_rating = book.ratings.aggregate(avg=Avg('score'))['avg']
    
    # Get recommendations
    recommended_books = recommend_books(book_id)
    
    context = {
        'book': book,
        'avg_rating': avg_rating,
        'recommended_books': recommended_books,
    }
    return render(request, 'book/book_detail.html', context)


def book_search(request):
    """
    API endpoint for book search (AJAX).
    """
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query)
    )[:10]  # Limit results
    
    results = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': str(book.price),
        'in_stock': book.is_in_stock(),
    } for book in books]
    
    return JsonResponse({'results': results})


def recommend_books(book_id, limit=5):
    """
    Recommendation System: Suggest books based on 'Customers who bought this also bought...'
    
    Logic:
    1. Find all customers who have this book in their cart items
    2. Find other books that these customers also have in their carts
    3. Rank books by frequency (how many customers bought them)
    4. Return top N recommendations
    
    Args:
        book_id: The ID of the book to find recommendations for
        limit: Maximum number of recommendations to return
    
    Returns:
        QuerySet of recommended Book objects
    """
    # Get the target book
    try:
        target_book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Book.objects.none()
    
    # Find all carts that contain the target book
    carts_with_book = CartItem.objects.filter(
        book_id=book_id
    ).values_list('cart_id', flat=True)
    
    # Find other books in those carts (excluding the target book)
    # Count how many times each book appears (popularity among similar buyers)
    recommended_book_ids = CartItem.objects.filter(
        cart_id__in=carts_with_book
    ).exclude(
        book_id=book_id
    ).values('book_id').annotate(
        frequency=Count('book_id')
    ).order_by('-frequency').values_list('book_id', flat=True)[:limit]
    
    # Get the actual book objects, preserving order
    recommended_books = Book.objects.filter(
        id__in=recommended_book_ids
    ).filter(stock_quantity__gt=0)  # Only in-stock books
    
    # If not enough recommendations, add some popular books
    if recommended_books.count() < limit:
        remaining = limit - recommended_books.count()
        popular_books = Book.objects.exclude(
            id=book_id
        ).exclude(
            id__in=recommended_book_ids
        ).filter(
            stock_quantity__gt=0
        ).annotate(
            order_count=Count('cart_items')
        ).order_by('-order_count')[:remaining]
        
        # Combine recommendations
        recommended_books = list(recommended_books) + list(popular_books)
    
    return recommended_books


def rate_book(request, book_id):
    """
    Handle book rating by a customer.
    """
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return JsonResponse({'error': 'Login required'}, status=401)
        
        score = request.POST.get('score')
        if not score or not score.isdigit() or int(score) < 1 or int(score) > 5:
            return JsonResponse({'error': 'Invalid rating score'}, status=400)
        
        rating, created = Rating.objects.update_or_create(
            customer_id=customer_id,
            book_id=book_id,
            defaults={'score': int(score)}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted successfully',
            'rating': rating.score
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
