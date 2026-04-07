from django.urls import path
from .views import (CreateReviewView, ProductReviewListView,
                    CustomerReviewListView, ProductAvgRatingView,
                    AdminReviewListView, AdminReviewDetailView)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer

class AllReviewsInternalView(APIView):
    """Trả về tất cả review - chỉ dành cho recommender-service gọi nội bộ."""
    def get(self, request):
        reviews = list(Review.objects.all().values('customer_id', 'product_type', 'product_id', 'rating'))
        for r in reviews:
            if r['product_type'] == 'book':
                r['book_id'] = r['product_id']
                
        return Response(reviews)

urlpatterns = [
    path('reviews/', CreateReviewView.as_view(), name='create-review'),
    path('reviews/books/<int:product_id>/', ProductReviewListView.as_view(), kwargs={'product_type': 'book'}, name='book-reviews'),
    path('reviews/product/<str:product_type>/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('reviews/mine/', CustomerReviewListView.as_view(), name='my-reviews'),
    path('reviews/avg-ratings/', ProductAvgRatingView.as_view(), name='avg-ratings'),
    path('reviews/admin/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('reviews/admin/<int:review_id>/', AdminReviewDetailView.as_view(), name='admin-review-detail'),
    path('reviews/all-internal/', AllReviewsInternalView.as_view(), name='all-reviews-internal'),
]
