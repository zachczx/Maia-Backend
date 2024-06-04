from django.urls import path, include
from .views import FileUploadView

urlpatterns = [
    path('file/', FileUploadView.as_view(), name='File Upload'),
]