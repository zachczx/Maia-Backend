from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import CustomerEngagement, Customer, KbEmbedding
from core.serializers import CustomerEngagementSerializer, CustomerSerializer, KbEmbeddingSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging

logger = logging.getLogger("django")

@method_decorator(csrf_exempt, name='dispatch')
class CustomerEngagementAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
    
@method_decorator(csrf_exempt, name='dispatch')
class CustomerAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            data = request.data
            if check_customer_exists(data.get('first_name'), 
                                     data.get('last_name'), 
                                     data.get('phone_number'), 
                                     data.get('country_code'), 
                                     data.get('email'))['exists']:
                raise ValidationError({'error': 'Customer already exists'})
            
            serializer = CustomerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return Response({'error': 'Failed to create customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class CustomerDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
        try:
            customer = self.get_object(customer_id)
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            return Response({'error': 'Failed to update customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, customer_id):
        try:
            customer = self.get_object(customer_id)
            customer.delete()
            return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            logger.error(f"Error deleting customer: {str(e)}")
            return Response({'error': 'Failed to delete customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def check_customer_exists(first_name, last_name, phone_number, country_code, email):
    try:
        customer = Customer.objects.get(
            Q(first_name__iexact=first_name) &
            Q(last_name__iexact=last_name) &
            Q(phone_number=phone_number) &
            Q(country_code=country_code) &
            Q(email__iexact=email)
        )
        return {
            'exists': True,
            'customer': CustomerSerializer(customer).data,
            'message': 'Customer exists'
        }
    except Customer.DoesNotExist:
        return {
            'exists': False,
            'message': 'Customer not found with the given details'
        }
        
@method_decorator(csrf_exempt, name='dispatch')
class KbEmbeddingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        embeddings = KbEmbedding.objects.all()
        serializer = KbEmbeddingSerializer(embeddings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = KbEmbeddingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class KbEmbeddingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, embedding_id):
        try:
            return KbEmbedding.objects.get(id=embedding_id)
        except KbEmbedding.DoesNotExist:
            raise ValidationError({'error': 'Embedding not found'})

    def get(self, request, embedding_id):
        embedding = self.get_object(embedding_id)
        serializer = KbEmbeddingSerializer(embedding)
        return Response(serializer.data)

    def put(self, request, embedding_id):
        embedding = self.get_object(embedding_id)
        serializer = KbEmbeddingSerializer(embedding, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, embedding_id):
        embedding = self.get_object(embedding_id)
        embedding.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)