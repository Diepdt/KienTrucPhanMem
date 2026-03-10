from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as django_settings
from django.db.models import Avg, Count
import requests as http_requests
import logging

from .models import Review
from .serializers import ReviewSerializer

logger = logging.getLogger(__name__)


def verify_customer_token(auth_header):
    try:
        resp = http_requests.get(
            f"{django_settings.CUSTOMER_SERVICE_URL}/api/customers/verify-token/",
            headers={'Authorization': auth_header}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return d.get('valid', False), d.get('customer')
    except Exception as e:
        logger.error(f"verify_customer error: {e}")
    return False, None


class CreateReviewView(APIView):
    """Khách hàng đánh giá sách."""

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        book_id = request.data.get('book_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not book_id or rating is None:
            return Response({'error': 'book_id và rating bắt buộc'}, status=400)

        # Kiểm tra nếu đã đánh giá rồi → cập nhật, chưa → tạo mới
        review, created = Review.objects.update_or_create(
            customer_id=customer['id'],
            book_id=book_id,
            defaults={'rating': int(rating), 'comment': comment}
        )
        action = 'Đánh giá đã được tạo.' if created else 'Đánh giá đã được cập nhật.'
        return Response({
            'message': action,
            'review': ReviewSerializer(review).data
        }, status=201 if created else 200)


class BookReviewListView(APIView):
    """Danh sách đánh giá của một cuốn sách."""

    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id).order_by('-created_at')
        stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
        return Response({
            'book_id': book_id,
            'avg_rating': round(stats['avg_rating'] or 0, 2),
            'total_reviews': stats['total'],
            'reviews': ReviewSerializer(reviews, many=True).data
        })


class CustomerReviewListView(APIView):
    """Danh sách đánh giá của một khách hàng."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)
        reviews = Review.objects.filter(customer_id=customer['id']).order_by('-created_at')
        return Response(ReviewSerializer(reviews, many=True).data)


class BookAvgRatingView(APIView):
    """API nội bộ: lấy điểm trung bình của nhiều cuốn sách."""

    def get(self, request):
        """GET /api/reviews/avg-ratings/?book_ids=1,2,3"""
        book_ids_str = request.query_params.get('book_ids', '')
        if not book_ids_str:
            return Response({'error': 'book_ids bắt buộc'}, status=400)
        try:
            book_ids = [int(b) for b in book_ids_str.split(',')]
        except ValueError:
            return Response({'error': 'book_ids không hợp lệ'}, status=400)

        result = {}
        for book_id in book_ids:
            stats = Review.objects.filter(book_id=book_id).aggregate(
                avg=Avg('rating'), count=Count('id'))
            result[book_id] = {
                'avg_rating': round(stats['avg'] or 0, 2),
                'count': stats['count']
            }
        return Response(result)
