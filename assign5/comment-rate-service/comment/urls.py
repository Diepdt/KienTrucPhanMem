from django.urls import path
from .views import (CreateReviewView, BookReviewListView,
                    CustomerReviewListView, BookAvgRatingView,
                    AdminReviewListView, AdminReviewDetailView)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer

class AllReviewsInternalView(APIView):
    """Trả về tất cả review - chỉ dành cho recommender-service gọi nội bộ."""
    def get(self, request):
        reviews = Review.objects.all().values('customer_id', 'book_id', 'rating')
        return Response(list(reviews))

urlpatterns = [
    path('reviews/', CreateReviewView.as_view(), name='create-review'),
    path('reviews/books/<int:book_id>/', BookReviewListView.as_view(), name='book-reviews'),
    path('reviews/mine/', CustomerReviewListView.as_view(), name='my-reviews'),
    path('reviews/avg-ratings/', BookAvgRatingView.as_view(), name='avg-ratings'),
    path('reviews/admin/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('reviews/admin/<int:review_id>/', AdminReviewDetailView.as_view(), name='admin-review-detail'),
    path('reviews/all-internal/', AllReviewsInternalView.as_view(), name='all-reviews-internal'),
]
