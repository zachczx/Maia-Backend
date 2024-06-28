from django.urls import path, include
from .views import TextQueryClassifierView, AudioQueryClassifierView, CategoryExcelProcessorView

urlpatterns = [
    path('query/text/', TextQueryClassifierView.as_view(), name='Text Query Classifier'),
    path('query/audio/', AudioQueryClassifierView.as_view(), name='Audio Query Classifier'),
    path('query/upload/category/', CategoryExcelProcessorView.as_view(), name='Upload categories'),
]