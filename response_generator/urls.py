from django.urls import path, include
from .views import ResponseGeneratorView

urlpatterns = [
    path('chat/', ResponseGeneratorView.as_view(), name='chatbot response generator'),
]