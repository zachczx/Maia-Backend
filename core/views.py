from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import CustomerEngagement, Customer
from core.serializers import CustomerEngagementSerializer, CustomerSerializer
import logging

logger = logging.getLogger("django")

@method_decorator(csrf_exempt, name='dispatch')
class CustomerEngagementAPIView(APIView):
    
    def get(self, request):
        engagements = CustomerEngagement.objects.all()
        serializer = CustomerEngagementSerializer(engagements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerEngagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Data saved successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CustomerEngagementDetailAPIView(APIView):

    def get_object(self, engagement_id):
        try:
            return CustomerEngagement.objects.get(id=engagement_id)
        except CustomerEngagement.DoesNotExist:
            raise ValidationError({'error': 'Customer engagement not found'})

    def get(self, request, engagement_id):
        engagement = self.get_object(engagement_id)
        serializer = CustomerEngagementSerializer(engagement)
        return Response(serializer.data)

    def put(self, request, engagement_id):
        engagement = self.get_object(engagement_id)
        serializer = CustomerEngagementSerializer(engagement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, engagement_id):
        engagement = self.get_object(engagement_id)
        engagement.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
    
def check_customer_exists(phone_number, first_name, last_name):
    exists = Customer.objects.filter(phone_number=phone_number, 
                                     first_name=first_name, 
                                     last_name=last_name).exists()
    return {'exists': exists}

@method_decorator(csrf_exempt, name='dispatch')
class CustomerAPIView(APIView):
    
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        if check_customer_exists(request.data.get('phone_number'), 
                                 request.data.get('first_name'), 
                                 request.data.get('last_name'))['exists']:
            return Response({'error': 'Customer already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Customer created successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CustomerDetailAPIView(APIView):

    def get_object(self, customer_id):
        try:
            return Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError({'error': 'Customer not found'})

    def get(self, request, customer_id):
        customer = self.get_object(customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, customer_id):
        customer = self.get_object(customer_id)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer_id):
        customer = self.get_object(customer_id)
        customer.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)