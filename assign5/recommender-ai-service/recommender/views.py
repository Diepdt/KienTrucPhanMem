from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as django_settings
import requests as http_requests
import logging
from collections import defaultdict

from .models import Recommendation

logger = logging.getLogger(__name__)


def fetch_all_books():
    """Lấy tất cả sách từ book-service."""
    try:
        resp = http_requests.get(
            f"{django_settings.BOOK_SERVICE_URL}/api/books/", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('results', resp.json()) if isinstance(resp.json(), dict) else resp.json()
    except Exception as e:
        logger.error(f"fetch_all_books error: {e}")
    return []


def fetch_all_reviews():
    """Lấy tất cả đánh giá từ comment-rate-service (gọi nội bộ)."""
    try:
        resp = http_requests.get(
            f"{django_settings.COMMENT_SERVICE_URL}/api/reviews/all-internal/", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"fetch_all_reviews error: {e}")
    return []


def fetch_customer_orders(customer_id):
    """Lấy đơn hàng của khách hàng - dùng internal endpoint."""
    try:
        resp = http_requests.get(
            f"{django_settings.ORDER_SERVICE_URL}/api/orders/customer/{customer_id}/internal/",
            timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"fetch_customer_orders error: {e}")
    return []


def compute_recommendations(customer_id):
    """
    Thuật toán gợi ý sách đơn giản (Content-based + Popularity):
    - Score = avg_rating * 0.6 + popularity_score * 0.4
    - Loại trừ sách khách hàng đã mua hoặc đã đánh giá
    - Trả về top 10 sách có điểm cao nhất
    """
    # 1. Lấy tất cả đánh giá
    reviews = fetch_all_reviews()

    # 2. Tính avg rating và số lượt đánh giá cho mỗi sách
    book_ratings = defaultdict(list)
    customer_rated_books = set()
    for review in reviews:
        book_id = review.get('book_id')
        rating = review.get('rating', 0)
        book_ratings[book_id].append(rating)
        if str(review.get('customer_id')) == str(customer_id):
            customer_rated_books.add(book_id)

    # 3. Lấy sách khách đã mua
    orders = fetch_customer_orders(customer_id)
    customer_bought_books = set()
    for order in orders:
        for item in order.get('items', []):
            customer_bought_books.add(item.get('book_id'))

    already_seen = customer_rated_books | customer_bought_books

    # 4. Tính max số đánh giá để normalize popularity
    max_reviews = max((len(v) for v in book_ratings.values()), default=1)

    # 5. Tính điểm cho từng sách
    recommendations = []
    for book_id, ratings in book_ratings.items():
        if book_id in already_seen:
            continue
        avg = sum(ratings) / len(ratings)
        popularity = len(ratings) / max_reviews
        score = avg * 0.7 + popularity * 0.3 * 5  # normalize to 5-scale

        # Chỉ gợi ý sách có avg_rating >= 3.5
        if avg >= 3.5:
            recommendations.append({
                'book_id': book_id,
                'score': round(score, 2),
                'avg_rating': round(avg, 2),
                'review_count': len(ratings),
                'reason': f'Đánh giá trung bình {round(avg, 1)}★ từ {len(ratings)} người dùng'
            })

    # 6. Sắp xếp theo điểm và trả top 10
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:10]


class RecommendationsView(APIView):
    """Gợi ý sách cho khách hàng."""

    def get(self, request, customer_id):
        recommendations = compute_recommendations(customer_id)

        # Lưu cache vào DB
        Recommendation.objects.filter(customer_id=customer_id).delete()
        for rec in recommendations:
            Recommendation.objects.create(
                customer_id=customer_id,
                book_id=rec['book_id'],
                score=rec['score'],
                reason=rec['reason']
            )

        return Response({
            'customer_id': customer_id,
            'total': len(recommendations),
            'recommendations': recommendations
        })


class CachedRecommendationsView(APIView):
    """Lấy gợi ý đã được cache."""

    def get(self, request, customer_id):
        recs = Recommendation.objects.filter(customer_id=customer_id).order_by('-score')
        if not recs.exists():
            # Tính lại nếu chưa có cache
            return RecommendationsView().get(request, customer_id)
        data = [{'book_id': r.book_id, 'score': r.score, 'reason': r.reason} for r in recs]
        return Response({'customer_id': customer_id, 'total': len(data), 'recommendations': data})
