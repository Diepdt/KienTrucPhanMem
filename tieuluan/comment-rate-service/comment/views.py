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


def verify_manager_token(auth_header):
    try:
        resp = http_requests.get(
            f"{django_settings.MANAGER_SERVICE_URL}/api/manager/verify-token/",
            headers={'Authorization': auth_header}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return d.get('valid', False), d.get('manager')
    except Exception as e:
        logger.error(f"verify_manager error: {e}")
    return False, None


def verify_staff_token(auth_header):
    try:
        resp = http_requests.get(
            f"{django_settings.STAFF_SERVICE_URL}/api/staff/verify-token/",
            headers={'Authorization': auth_header}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return d.get('valid', False), d.get('staff')
    except Exception as e:
        logger.error(f"verify_staff error: {e}")
    return False, None


def verify_admin_token(auth_header):
    valid_manager, manager = verify_manager_token(auth_header)
    if valid_manager:
        return True, manager

    valid_staff, staff = verify_staff_token(auth_header)
    if valid_staff:
        return True, staff

    return False, None


def has_customer_purchased_product(customer_id, product_type, product_id):
    try:
        resp = http_requests.get(
            f"{django_settings.ORDER_SERVICE_URL}/api/orders/customer/{customer_id}/internal/",
            timeout=5
        )
        if resp.status_code != 200:
            return False

        orders = resp.json() if isinstance(resp.json(), list) else []
        for order in orders:
            if order.get('status') != 'delivered':
                continue
            for item in order.get('items', []):
                if item.get('product_type', 'book') == product_type and int(item.get('product_id', 0)) == int(product_id):
                    return True
    except Exception as e:
        logger.error(f"has_customer_purchased_product error: {e}")

    return False


class CreateReviewView(APIView):
    """Khách hàng đánh giá sản phẩm."""

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        product_type = request.data.get('product_type', 'book')
        product_id = request.data.get('product_id')
        if not product_id and request.data.get('book_id'):
            product_id = request.data.get('book_id')

        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not product_id or rating is None:
            return Response({'error': 'product_id và rating bắt buộc'}, status=400)

        if not has_customer_purchased_product(customer['id'], product_type, product_id):
            return Response({'error': 'Bạn chỉ có thể đánh giá sản phẩm trong đơn hàng đã giao.'}, status=403)

        review, created = Review.objects.update_or_create(
            customer_id=customer['id'],
            product_type=product_type,
            product_id=product_id,
            defaults={'rating': int(rating), 'comment': comment}
        )
        action = 'Đánh giá đã được tạo.' if created else 'Đánh giá đã được cập nhật.'
        return Response({
            'message': action,
            'review': ReviewSerializer(review).data
        }, status=201 if created else 200)


class AdminReviewListView(APIView):
    """Manager/Staff xem thống kê và danh sách đánh giá."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, _admin = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        reviews = Review.objects.all().order_by('-created_at')
        stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))

        distribution = {str(i): reviews.filter(rating=i).count() for i in range(1, 6)}

        top_items_qs = (
            Review.objects.values('product_type', 'product_id')
            .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))
            .order_by('-avg_rating', '-total_reviews')[:10]
        )

        return Response({
            'summary': {
                'total_reviews': stats['total'] or 0,
                'avg_rating': round(stats['avg_rating'] or 0, 2),
                'rating_distribution': distribution,
            },
            'top_products': list(top_items_qs),
            'results': ReviewSerializer(reviews, many=True).data,
        })


class AdminReviewDetailView(APIView):
    """Không cho phép xóa đánh giá từ trang quản trị."""

    def delete(self, request, review_id):
        return Response(
            {'error': 'Chức năng xóa đánh giá đã bị vô hiệu hóa để đảm bảo công bằng.'},
            status=403
        )


class ProductReviewListView(APIView):
    """Danh sách đánh giá của một sản phẩm."""

    def get(self, request, product_type, product_id):
        reviews = Review.objects.filter(product_type=product_type, product_id=product_id).order_by('-created_at')
        stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
        return Response({
            'product_type': product_type,
            'product_id': product_id,
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


class ProductAvgRatingView(APIView):
    """API nội bộ: lấy điểm trung bình của nhiều sản phẩm."""

    def get(self, request):
        """GET /api/reviews/avg-ratings/?product_type=book&product_ids=1,2,3"""
        product_ids_str = request.query_params.get('product_ids', '')
        if not product_ids_str:
            product_ids_str = request.query_params.get('book_ids', '')

        if not product_ids_str:
            return Response({'error': 'product_ids bắt buộc'}, status=400)
            
        product_type = request.query_params.get('product_type', 'book')
        try:
            ids = [int(b) for b in product_ids_str.split(',')]
        except ValueError:
            return Response({'error': 'product_ids không hợp lệ'}, status=400)

        result = {}
        for p_id in ids:
            stats = Review.objects.filter(product_type=product_type, product_id=p_id).aggregate(
                avg=Avg('rating'), count=Count('id'))
            result[p_id] = {
                'avg_rating': round(stats['avg'] or 0, 2),
                'count': stats['count']
            }
        return Response(result)
