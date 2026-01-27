from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Sum, F
from django.core.paginator import Paginator
from store.models import Book, CartItem, Rating, OrderItem


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
    Advanced Recommendation System based on:
    1. Purchase History: "Customers who bought this also bought..."
    2. Rating Similarity: Books highly rated by users who also rated this book highly
    
    Algorithm:
    - Weight 1 (Purchase): Find books commonly purchased together (via CartItem & OrderItem)
    - Weight 2 (Rating): Find books with high ratings from users who gave this book high ratings
    - Combine scores and rank by weighted sum
    
    Args:
        book_id: The ID of the book to find recommendations for
        limit: Maximum number of recommendations to return
    
    Returns:
        List of recommended Book objects
    """
    from collections import defaultdict
    
    # Get the target book
    try:
        target_book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return []
    
    # Dictionary to store recommendation scores
    recommendation_scores = defaultdict(float)
    
    # ==========================================
    # STRATEGY 1: Purchase History (CartItem)
    # "Customers who bought this also bought..."
    # ==========================================
    
    # Find all carts that contain the target book
    carts_with_book = CartItem.objects.filter(
        book_id=book_id
    ).values_list('cart_id', flat=True)
    
    # Find other books in those carts with frequency count
    cart_recommendations = CartItem.objects.filter(
        cart_id__in=carts_with_book
    ).exclude(
        book_id=book_id
    ).values('book_id').annotate(
        frequency=Count('book_id')
    )
    
    for rec in cart_recommendations:
        # Weight: 3.0 for purchase history (most important signal)
        recommendation_scores[rec['book_id']] += rec['frequency'] * 3.0
    
    # ==========================================
    # STRATEGY 2: Order History (OrderItem) 
    # Based on actual completed purchases
    # ==========================================
    
    # Find customers who ordered this book
    customers_who_ordered = OrderItem.objects.filter(
        book_id=book_id
    ).values_list('order__customer_id', flat=True).distinct()
    
    # Find other books these customers ordered
    order_recommendations = OrderItem.objects.filter(
        order__customer_id__in=customers_who_ordered
    ).exclude(
        book_id=book_id
    ).values('book_id').annotate(
        frequency=Count('book_id')
    )
    
    for rec in order_recommendations:
        # Weight: 4.0 for actual purchases (strongest signal)
        recommendation_scores[rec['book_id']] += rec['frequency'] * 4.0
    
    # ==========================================
    # STRATEGY 3: Rating-based Collaborative Filtering
    # "Users who rated this highly also rated these highly"
    # ==========================================
    
    # Find customers who gave this book a high rating (4 or 5)
    customers_who_liked = Rating.objects.filter(
        book_id=book_id,
        score__gte=4
    ).values_list('customer_id', flat=True)
    
    # Find other books these customers rated highly
    rating_recommendations = Rating.objects.filter(
        customer_id__in=customers_who_liked,
        score__gte=4
    ).exclude(
        book_id=book_id
    ).values('book_id').annotate(
        total_score=Sum('score'),
        count=Count('book_id')
    )
    
    for rec in rating_recommendations:
        # Weight: 2.0 for rating similarity, multiplied by avg score
        avg_score = rec['total_score'] / rec['count'] if rec['count'] > 0 else 0
        recommendation_scores[rec['book_id']] += rec['count'] * avg_score * 2.0
    
    # ==========================================
    # STRATEGY 4: High-rated books in general (fallback)
    # ==========================================
    
    if len(recommendation_scores) < limit:
        # Add highly-rated books as fallback
        highly_rated = Rating.objects.exclude(
            book_id=book_id
        ).values('book_id').annotate(
            avg_rating=Avg('score'),
            rating_count=Count('book_id')
        ).filter(
            avg_rating__gte=4.0,
            rating_count__gte=1
        )
        
        for rec in highly_rated:
            if rec['book_id'] not in recommendation_scores:
                # Lower weight for general popularity
                recommendation_scores[rec['book_id']] += rec['avg_rating'] * rec['rating_count'] * 0.5
    
    # ==========================================
    # FINAL: Sort and get top recommendations
    # ==========================================
    
    # Sort by score descending
    sorted_recommendations = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Get book IDs
    recommended_ids = [book_id for book_id, score in sorted_recommendations[:limit * 2]]
    
    # Fetch books that are in stock
    recommended_books = list(
        Book.objects.filter(
            id__in=recommended_ids,
            stock_quantity__gt=0
        )[:limit]
    )
    
    # If still not enough, add popular books by order count
    if len(recommended_books) < limit:
        remaining = limit - len(recommended_books)
        existing_ids = [b.id for b in recommended_books]
        existing_ids.append(book_id)
        
        popular_books = Book.objects.exclude(
            id__in=existing_ids
        ).filter(
            stock_quantity__gt=0
        ).annotate(
            popularity=Count('order_items') + Count('cart_items')
        ).order_by('-popularity')[:remaining]
        
        recommended_books.extend(list(popular_books))
    
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
