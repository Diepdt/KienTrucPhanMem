"""
Recommendation Controller URLs
"""

from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('', views.recommendations_view, name='list'),
    path('generate/', views.generate_recommendations, name='generate'),
    path('track-click/<int:item_id>/', views.track_click, name='track_click'),
    path('feedback/', views.submit_feedback, name='feedback'),
    path('track/<int:book_id>/<str:behavior_type>/', views.track_behavior, name='track_behavior'),
]
