from django.urls import path
from .views import CustomerEngagementAPIView, CustomerEngagementDetailAPIView, CustomerAPIView, CustomerDetailAPIView, KbEmbeddingAPIView, KbEmbeddingDetailAPIView

urlpatterns = [
    path('engagement/', CustomerEngagementAPIView.as_view(), name='customer_engagements'),
    path('engagement/<int:engagement_id>/', CustomerEngagementDetailAPIView.as_view(), name='customer_engagement_detail'),
    path('customer/', CustomerAPIView.as_view(), name='customer'),
    path('customer/<int:customer_id>/', CustomerDetailAPIView.as_view(), name='customer_detail'),
    path('kbembedding/', KbEmbeddingAPIView.as_view(), name='kbembedding'),
    path('kbembedding/<int:embedding_id>/', KbEmbeddingDetailAPIView.as_view(), name='kbembedding_detail'),
]