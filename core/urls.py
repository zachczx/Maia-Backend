from django.urls import path
from .views import CustomerEngagementAPIView, CustomerEngagementDetailAPIView

urlpatterns = [
    path('engagement/', CustomerEngagementAPIView.as_view(), name='customer_engagements'),
    path('engagement/<int:engagement_id>/', CustomerEngagementDetailAPIView.as_view(), name='customer_engagement_detail'),
]