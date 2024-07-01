from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import CustomerProfile, Customer
from core.serializers import CustomerProfileSerializer, CustomerSerialize
import logging

logger = logging.getLogger("django")

@method_decorator(csrf_exempt, name='dispatch')
class CustomerProfileAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = TextQueryClassifierSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data.get('query', None)
            history = serializer.validated_data.get('history', None)
            if history:
                history = [tuple(item) for item in history]
            
            response = query_classifier(query, history)
            json_response = asdict(response)
            
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)