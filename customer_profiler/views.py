from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import CustomerProfileSerializer
from .utils.data_models import ProfilingRequest
from .services.customer_search_service import search_customer
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger("django")

@method_decorator(csrf_exempt, name='dispatch')
class CustomerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data.get('first_name', None)
            last_name = serializer.validated_data.get('last_name', None)
            country_code = serializer.validated_data.get('country_code', None)
            phone_number = serializer.validated_data.get('phone_number', None)
            email = serializer.validated_data.get("email", None)

            customer = ProfilingRequest(first_name, last_name, country_code, phone_number, email)
            response = search_customer(customer)
            
            return Response(data=response.to_json(), status=status.HTTP_200_OK)
        else:
            logger.info("error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)