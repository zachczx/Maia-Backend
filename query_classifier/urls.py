from django.urls import path, include
from .views import QueryClassifierView

urlpatterns = [
    path('query/', QueryClassifierView.as_view(), name='Query Classifier'),
]