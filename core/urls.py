from django.urls import path, include
from .views import KbResourceView

urlpatterns = [
    path('kbresource/', KbResourceView.as_view(), name='KbResource'),
]