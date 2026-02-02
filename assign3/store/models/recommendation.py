"""
Recommendation Module - AI-Powered Book Recommendations
Uses OpenAI API for intelligent book suggestions based on user behavior

Contains 5 Models:
1. RecommendationEngine - Configuration for recommendation system
2. UserBehavior - Tracks user interactions and preferences
3. Recommendation - Main recommendation record
4. RecommendationItem - Individual recommended books
5. RecommendationFeedback - User feedback on recommendations
"""

import uuid
import json
from decimal import Decimal
from django.db import models
from django.conf import settings
from store.models.base import TimeStampedModel


class RecommendationEngine(TimeStampedModel):
    """
    Configuration for the recommendation engine.
    Stores API settings and algorithm parameters.
    
    Relationships:
    - Has many Recommendations (1-N)
    """
    ENGINE_TYPES = [
        ('openai', 'OpenAI GPT'),
        ('collaborative', 'Collaborative Filtering'),
        ('content', 'Content-Based'),
        ('hybrid', 'Hybrid'),
    ]
    
    engine_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    engine_type = models.CharField(max_length=20, choices=ENGINE_TYPES, default='openai')
    model_name = models.CharField(max_length=50, default='gpt-3.5-turbo')  # OpenAI model
    max_recommendations = models.PositiveIntegerField(default=5)
    temperature = models.FloatField(default=0.7)  # OpenAI temperature
    is_active = models.BooleanField(default=True)
    api_key_configured = models.BooleanField(default=False)
    
    # Algorithm weights
    purchase_weight = models.FloatField(default=0.4)
    review_weight = models.FloatField(default=0.3)
    browse_weight = models.FloatField(default=0.2)
    wishlist_weight = models.FloatField(default=0.1)
    
    class Meta:
        db_table = 'recommendation_engine'
        verbose_name = 'Recommendation Engine'
        verbose_name_plural = 'Recommendation Engines'
    
    def __str__(self):
        return f"{self.name} ({self.engine_type})"


class UserBehavior(TimeStampedModel):
    """
    Tracks user interactions and preferences for recommendation analysis.
    
    Relationships:
    - Belongs to Customer (N-1)
    - Belongs to Book (N-1, optional)
    """
    BEHAVIOR_TYPES = [
        ('view', 'Viewed Book'),
        ('search', 'Searched'),
        ('add_cart', 'Added to Cart'),
        ('purchase', 'Purchased'),
        ('review', 'Reviewed'),
        ('wishlist', 'Added to Wishlist'),
        ('remove_cart', 'Removed from Cart'),
    ]
    
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='behaviors'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_behaviors'
    )
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPES)
    search_query = models.CharField(max_length=255, blank=True, null=True)
    category_viewed = models.ForeignKey(
        'store.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)  # Extra data
    
    class Meta:
        db_table = 'user_behavior'
        verbose_name = 'User Behavior'
        verbose_name_plural = 'User Behaviors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'behavior_type']),
            models.Index(fields=['book', 'behavior_type']),
        ]
    
    def __str__(self):
        book_title = self.book.title if self.book else 'N/A'
        return f"{self.customer} - {self.behavior_type} - {book_title}"


class Recommendation(TimeStampedModel):
    """
    Main recommendation record storing AI-generated suggestions.
    
    Relationships:
    - Belongs to Customer (N-1)
    - Belongs to RecommendationEngine (N-1)
    - Has many RecommendationItems (1-N)
    - Has many RecommendationFeedbacks (1-N)
    """
    recommendation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    engine = models.ForeignKey(
        RecommendationEngine,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recommendations'
    )
    
    # User history snapshot used for this recommendation
    user_history = models.JSONField(default=dict)
    
    # AI-generated recommendation list
    recommended_list = models.JSONField(default=list)
    
    # AI response metadata
    ai_prompt = models.TextField(blank=True, null=True)
    ai_response = models.TextField(blank=True, null=True)
    tokens_used = models.PositiveIntegerField(default=0)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Validity
    is_valid = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'recommendation'
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recommendation for {self.customer} - {self.status}"
    
    def analyze_behavior(self):
        """
        Fetches user's past Orders and Reviews, formats them,
        and updates the user_history field.
        """
        from store.models.order import Order, OrderItem, Review, Rating
        from store.models.product import Book, Category
        
        history = {
            'purchases': [],
            'reviews': [],
            'ratings': [],
            'categories': [],
            'authors': [],
            'recent_views': [],
        }
        
        # Get purchase history from Orders
        orders = Order.objects.filter(
            customer=self.customer,
            status__in=['completed', 'delivered', 'shipped']
        ).prefetch_related('items__book__authors', 'items__book__category')
        
        for order in orders[:10]:  # Last 10 orders
            for item in order.items.all():
                book = item.book
                if book:
                    purchase_data = {
                        'book_id': book.id,
                        'title': book.title,
                        'authors': [a.name for a in book.authors.all()],
                        'category': book.category.name if book.category else None,
                        'price': str(book.price),
                        'purchased_at': order.created_at.isoformat(),
                    }
                    history['purchases'].append(purchase_data)
                    
                    # Collect categories
                    if book.category and book.category.name not in history['categories']:
                        history['categories'].append(book.category.name)
                    
                    # Collect authors
                    for author in book.authors.all():
                        if author.name not in history['authors']:
                            history['authors'].append(author.name)
        
        # Get reviews
        reviews = Review.objects.filter(customer=self.customer).select_related('book')
        for review in reviews[:10]:
            if review.book:
                history['reviews'].append({
                    'book_id': review.book.id,
                    'title': review.book.title,
                    'content': review.content[:200] if review.content else '',
                })
        
        # Get ratings
        ratings = Rating.objects.filter(customer=self.customer).select_related('book')
        for rating in ratings[:10]:
            if rating.book:
                history['ratings'].append({
                    'book_id': rating.book.id,
                    'title': rating.book.title,
                    'score': rating.score,
                })
        
        # Get recent views from UserBehavior
        views = UserBehavior.objects.filter(
            customer=self.customer,
            behavior_type='view',
            book__isnull=False
        ).select_related('book')[:10]
        
        for view in views:
            history['recent_views'].append({
                'book_id': view.book.id,
                'title': view.book.title,
            })
        
        self.user_history = history
        self.save(update_fields=['user_history'])
        
        return history
    
    def generate_recommendation(self):
        """
        Calls OpenAI API to generate book recommendations based on user history.
        Falls back to simple algorithm if no API key is configured.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Analyze behavior if not done
        if not self.user_history:
            self.analyze_behavior()
        
        self.status = 'processing'
        self.save(update_fields=['status'])
        
        # Check API key
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key or api_key == '':
            # Use fallback algorithm instead of OpenAI
            return self._generate_fallback_recommendations()
        
        try:
            # Build prompt
            prompt = self._build_prompt()
            self.ai_prompt = prompt
            
            # Call OpenAI API
            client = openai.OpenAI(api_key=api_key)
            
            engine = self.engine
            model = engine.model_name if engine else 'gpt-3.5-turbo'
            temperature = engine.temperature if engine else 0.7
            max_recommendations = engine.max_recommendations if engine else 5
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert bookstore consultant. 
                        Based on the customer's reading history, preferences, and behavior, 
                        recommend books they would enjoy. 
                        Always respond in valid JSON format with a list of book recommendations."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=1000
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            self.ai_response = ai_response
            self.tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Extract recommendations from response
            recommendations = self._parse_ai_response(ai_response)
            self.recommended_list = recommendations
            
            # Create RecommendationItems
            self._create_recommendation_items(recommendations)
            
            # Set expiration (7 days)
            self.expires_at = timezone.now() + timedelta(days=7)
            self.status = 'completed'
            self.save()
            
            return recommendations
            
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            self.save()
            return None
    
    def _build_prompt(self):
        """Build the prompt for OpenAI based on user history."""
        from store.models.product import Book
        
        history = self.user_history
        max_recs = self.engine.max_recommendations if self.engine else 5
        
        prompt_parts = [
            f"Please recommend {max_recs} books for a customer with the following profile:\n"
        ]
        
        # Add purchase history
        if history.get('purchases'):
            prompt_parts.append("\n## Recently Purchased Books:")
            for p in history['purchases'][:5]:
                prompt_parts.append(f"- {p['title']} by {', '.join(p['authors'])}")
        
        # Add favorite categories
        if history.get('categories'):
            prompt_parts.append(f"\n## Favorite Categories: {', '.join(history['categories'][:5])}")
        
        # Add favorite authors
        if history.get('authors'):
            prompt_parts.append(f"\n## Favorite Authors: {', '.join(history['authors'][:5])}")
        
        # Add ratings
        if history.get('ratings'):
            high_rated = [r for r in history['ratings'] if r['score'] >= 4]
            if high_rated:
                prompt_parts.append("\n## Highly Rated Books (4-5 stars):")
                for r in high_rated[:5]:
                    prompt_parts.append(f"- {r['title']} ({r['score']} stars)")
        
        # Get available books in store
        available_books = Book.objects.filter(
            is_active=True,
            stock_quantity__gt=0
        ).exclude(
            id__in=[p['book_id'] for p in history.get('purchases', [])]
        ).values('id', 'title', 'price')[:50]
        
        if available_books:
            prompt_parts.append("\n## Available Books in Store (choose from these):")
            for book in available_books:
                prompt_parts.append(f"- ID:{book['id']} - {book['title']} - {book['price']}đ")
        
        prompt_parts.append(f"""
\n## Instructions:
1. Based on the customer's history, recommend exactly {max_recs} books from the available list.
2. Explain briefly why each book is recommended.
3. Response MUST be in this JSON format:
{{
    "recommendations": [
        {{
            "book_id": <id>,
            "title": "<book title>",
            "reason": "<why this book is recommended>"
        }}
    ]
}}
""")
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response_text):
        """Parse the AI response to extract recommendations."""
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('recommendations', [])
        except json.JSONDecodeError:
            pass
        
        # Fallback: return empty list
        return []
    
    def _create_recommendation_items(self, recommendations):
        """Create RecommendationItem records for each recommended book."""
        from store.models.product import Book
        
        for idx, rec in enumerate(recommendations):
            book_id = rec.get('book_id')
            if book_id:
                try:
                    book = Book.objects.get(id=book_id)
                    RecommendationItem.objects.create(
                        recommendation=self,
                        book=book,
                        rank=idx + 1,
                        reason=rec.get('reason', ''),
                        confidence_score=rec.get('confidence', 0.8 - (idx * 0.1))
                    )
                except Book.DoesNotExist:
                    pass
    
    def _generate_fallback_recommendations(self):
        """
        Generate recommendations using a simple algorithm when OpenAI is not available.
        Based on: same category, same author, popular books, highly rated.
        """
        from store.models.product import Book, Category
        from django.db.models import Avg, Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        history = self.user_history
        max_recs = self.engine.max_recommendations if self.engine else 5
        
        # Collect book IDs already purchased/viewed
        exclude_ids = set()
        for p in history.get('purchases', []):
            exclude_ids.add(p.get('book_id'))
        for v in history.get('recent_views', []):
            exclude_ids.add(v.get('book_id'))
        
        recommendations = []
        scores = {}  # book_id -> score
        
        # Strategy 1: Books from same categories (weight: 3.0)
        categories = history.get('categories', [])
        if categories:
            same_category_books = Book.objects.filter(
                is_active=True,
                stock_quantity__gt=0,
                category__name__in=categories
            ).exclude(id__in=exclude_ids)[:20]
            
            for book in same_category_books:
                scores[book.id] = scores.get(book.id, 0) + 3.0
        
        # Strategy 2: Books from same authors (weight: 4.0)
        authors = history.get('authors', [])
        if authors:
            same_author_books = Book.objects.filter(
                is_active=True,
                stock_quantity__gt=0,
                authors__name__in=authors
            ).exclude(id__in=exclude_ids).distinct()[:20]
            
            for book in same_author_books:
                scores[book.id] = scores.get(book.id, 0) + 4.0
        
        # Strategy 3: Highly rated books (weight: 2.0)
        from store.models.order import Rating
        popular_rated = Book.objects.filter(
            is_active=True,
            stock_quantity__gt=0
        ).exclude(id__in=exclude_ids).annotate(
            avg_rating=Avg('ratings__score'),
            rating_count=Count('ratings')
        ).filter(rating_count__gte=1).order_by('-avg_rating')[:20]
        
        for book in popular_rated:
            weight = 2.0 * (book.avg_rating / 5.0 if book.avg_rating else 0.5)
            scores[book.id] = scores.get(book.id, 0) + weight
        
        # Strategy 4: Popular/New books (weight: 1.0)
        new_books = Book.objects.filter(
            is_active=True,
            stock_quantity__gt=0
        ).exclude(id__in=exclude_ids).order_by('-created_at')[:10]
        
        for book in new_books:
            scores[book.id] = scores.get(book.id, 0) + 1.0
        
        # Sort by score and get top recommendations
        sorted_books = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:max_recs]
        
        # Build recommendation reasons
        reason_templates = {
            'category': 'Vì bạn thích thể loại {category}',
            'author': 'Từ tác giả bạn yêu thích',
            'popular': 'Sách được đánh giá cao',
            'new': 'Sách mới phổ biến',
        }
        
        for book_id, score in sorted_books:
            try:
                book = Book.objects.get(id=book_id)
                
                # Determine reason based on what contributed to the score
                reason = 'Gợi ý dựa trên sở thích của bạn'
                if book.category and book.category.name in categories:
                    reason = f"Vì bạn thích thể loại {book.category.name}"
                elif any(a.name in authors for a in book.authors.all()):
                    reason = "Từ tác giả bạn yêu thích"
                
                recommendations.append({
                    'book_id': book.id,
                    'title': book.title,
                    'reason': reason,
                    'confidence': min(score / 10.0, 0.95)  # Normalize to 0-1
                })
            except Book.DoesNotExist:
                continue
        
        # If not enough recommendations, add random popular books
        if len(recommendations) < max_recs:
            remaining = max_recs - len(recommendations)
            existing_ids = [r['book_id'] for r in recommendations]
            
            fallback_books = Book.objects.filter(
                is_active=True,
                stock_quantity__gt=0
            ).exclude(
                id__in=exclude_ids
            ).exclude(
                id__in=existing_ids
            ).order_by('?')[:remaining]
            
            for book in fallback_books:
                recommendations.append({
                    'book_id': book.id,
                    'title': book.title,
                    'reason': 'Có thể bạn sẽ thích',
                    'confidence': 0.5
                })
        
        # Save results
        self.recommended_list = recommendations
        self.ai_response = 'Generated using fallback algorithm (no OpenAI API key)'
        self.expires_at = timezone.now() + timedelta(days=7)
        self.status = 'completed'
        self.save()
        
        # Create recommendation items
        self._create_recommendation_items(recommendations)
        
        return recommendations
    
    def get_recommended_books(self):
        """Get the actual Book objects from recommendations."""
        return [item.book for item in self.items.all().select_related('book')]


class RecommendationItem(TimeStampedModel):
    """
    Individual recommended book within a Recommendation.
    
    Relationships:
    - Belongs to Recommendation (N-1)
    - Belongs to Book (N-1)
    """
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='recommendation_items'
    )
    rank = models.PositiveIntegerField(default=1)  # Position in list
    reason = models.TextField(blank=True)  # AI explanation
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    
    # Tracking
    was_clicked = models.BooleanField(default=False)
    was_purchased = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'recommendation_item'
        verbose_name = 'Recommendation Item'
        verbose_name_plural = 'Recommendation Items'
        ordering = ['rank']
        unique_together = ['recommendation', 'book']
    
    def __str__(self):
        return f"#{self.rank} - {self.book.title}"
    
    def mark_clicked(self):
        """Mark this item as clicked."""
        from django.utils import timezone
        if not self.was_clicked:
            self.was_clicked = True
            self.clicked_at = timezone.now()
            self.save(update_fields=['was_clicked', 'clicked_at'])
    
    def mark_purchased(self):
        """Mark this item as purchased."""
        from django.utils import timezone
        self.was_purchased = True
        self.purchased_at = timezone.now()
        self.save(update_fields=['was_purchased', 'purchased_at'])


class RecommendationFeedback(TimeStampedModel):
    """
    User feedback on recommendations for improving the system.
    
    Relationships:
    - Belongs to Recommendation (N-1)
    - Belongs to Customer (N-1)
    - Belongs to Book (N-1, optional)
    """
    FEEDBACK_TYPES = [
        ('like', 'Liked'),
        ('dislike', 'Disliked'),
        ('not_interested', 'Not Interested'),
        ('already_read', 'Already Read'),
        ('will_buy', 'Will Buy Later'),
    ]
    
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='recommendation_feedbacks'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 overall rating
    
    class Meta:
        db_table = 'recommendation_feedback'
        verbose_name = 'Recommendation Feedback'
        verbose_name_plural = 'Recommendation Feedbacks'
        unique_together = ['recommendation', 'customer', 'book']
    
    def __str__(self):
        return f"{self.customer} - {self.feedback_type}"
