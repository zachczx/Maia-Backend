from django.urls import path, include
from .views import FileUploadView, ResourceView

urlpatterns = [
    path('file/', FileUploadView.as_view(), name='File Upload'),
    path('resource/', ResourceView.as_view(), name='Resource List'),
    path('resource/<int:pk>/', ResourceView.as_view(), name='Resouce Detail'),
]