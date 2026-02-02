"""
Recommendation Controller - Views for AI-powered book recommendations
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from store.models import (
    Customer, Book, Recommendation, RecommendationEngine,
    RecommendationItem, RecommendationFeedback, UserBehavior
)


def get_current_customer(request):
    """Get current logged-in customer."""
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            return Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            pass
    return None


def recommendations_view(request):
    """
    Display personalized recommendations for the customer.
    """
    customer = get_current_customer(request)
    if not customer:
        messages.warning(request, 'Please login to see personalized recommendations.')
        return redirect('customer:login')
    
    # Get or create recommendation
    recommendation = Recommendation.objects.filter(
        customer=customer,
        status='completed',
        is_valid=True,
        expires_at__gt=timezone.now()
    ).first()
    
    # Get recommended books
    recommended_items = []
    if recommendation:
        recommended_items = recommendation.items.all().select_related('book', 'book__category')
    
    # Get popular books as fallback
    popular_books = Book.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).order_by('-created_at')[:10]
    
    context = {
        'recommendation': recommendation,
        'recommended_items': recommended_items,
        'popular_books': popular_books,
    }
    
    return render(request, 'recommendation/recommendations.html', context)


@csrf_exempt
def generate_recommendations(request):
    """
    Generate new AI recommendations for the customer.
    """
    customer = get_current_customer(request)
    if not customer:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Please login first'})
        messages.error(request, 'Please login to generate recommendations.')
        return redirect('customer:login')
    
    try:
        # Get active recommendation engine
        engine = RecommendationEngine.objects.filter(is_active=True).first()
        
        # Create new recommendation
        recommendation = Recommendation.objects.create(
            customer=customer,
            engine=engine,
            status='pending'
        )
        
        # Analyze behavior
        recommendation.analyze_behavior()
        
        # Generate recommendations
        result = recommendation.generate_recommendation()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result:
                items = []
                for item in recommendation.items.all().select_related('book'):
                    items.append({
                        'id': item.id,
                        'book_id': item.book.id,
                        'title': item.book.title,
                        'price': str(item.book.price),
                        'reason': item.reason,
                        'rank': item.rank,
                    })
                return JsonResponse({
                    'success': True,
                    'recommendation_id': str(recommendation.recommendation_id),
                    'items': items
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': recommendation.error_message or 'Failed to generate recommendations'
                })
        
        if result:
            messages.success(request, 'New recommendations generated successfully!')
        else:
            messages.error(request, f'Failed to generate recommendations: {recommendation.error_message}')
        
        return redirect('recommendation:list')
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error: {str(e)}')
        return redirect('recommendation:list')


@require_POST
def track_click(request, item_id):
    """
    Track when a user clicks on a recommended item.
    """
    customer = get_current_customer(request)
    if not customer:
        return JsonResponse({'success': False, 'error': 'Not logged in'})
    
    try:
        item = RecommendationItem.objects.get(
            id=item_id,
            recommendation__customer=customer
        )
        item.mark_clicked()
        
        # Also record as user behavior
        UserBehavior.objects.create(
            customer=customer,
            book=item.book,
            behavior_type='view',
            metadata={'source': 'recommendation', 'recommendation_id': str(item.recommendation.recommendation_id)}
        )
        
        return JsonResponse({'success': True})
    except RecommendationItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


@require_POST
def submit_feedback(request):
    """
    Submit feedback on a recommendation.
    """
    customer = get_current_customer(request)
    if not customer:
        return JsonResponse({'success': False, 'error': 'Not logged in'})
    
    recommendation_id = request.POST.get('recommendation_id')
    book_id = request.POST.get('book_id')
    feedback_type = request.POST.get('feedback_type')
    comment = request.POST.get('comment', '')
    rating = request.POST.get('rating')
    
    try:
        recommendation = Recommendation.objects.get(
            recommendation_id=recommendation_id,
            customer=customer
        )
        
        book = None
        if book_id:
            book = Book.objects.get(id=book_id)
        
        feedback, created = RecommendationFeedback.objects.update_or_create(
            recommendation=recommendation,
            customer=customer,
            book=book,
            defaults={
                'feedback_type': feedback_type,
                'comment': comment,
                'rating': int(rating) if rating else None,
            }
        )
        
        return JsonResponse({'success': True, 'created': created})
    except (Recommendation.DoesNotExist, Book.DoesNotExist) as e:
        return JsonResponse({'success': False, 'error': str(e)})


def track_behavior(request, book_id, behavior_type):
    """
    Track user behavior for recommendation improvements.
    Called via AJAX when user interacts with books.
    """
    customer = get_current_customer(request)
    if not customer:
        return JsonResponse({'success': False})
    
    try:
        book = Book.objects.get(id=book_id)
        
        UserBehavior.objects.create(
            customer=customer,
            book=book,
            behavior_type=behavior_type,
            session_id=request.session.session_key
        )
        
        return JsonResponse({'success': True})
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found'})
