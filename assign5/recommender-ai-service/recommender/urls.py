from django.urls import path
from .views import RecommendationsView, CachedRecommendationsView

urlpatterns = [
    path('recommendations/<int:customer_id>/', RecommendationsView.as_view(), name='recommendations'),
    path('recommendations/<int:customer_id>/cached/', CachedRecommendationsView.as_view(), name='recommendations-cached'),
]
