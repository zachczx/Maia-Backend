from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import CustomerEngagement, Customer, KbEmbedding
from core.serializers import CustomerEngagementSerializer, CustomerSerializer, KbEmbeddingSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import JsonResponse
from typing import Dict, Any
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger("django")

@swagger_auto_schema(
    operation_description="Health check endpoint to verify if the service is up.",
    responses={
        200: openapi.Response(
            description="Service is up and running",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='Service status')
                }
            )
        )
    }
)
def health_check(request: Request) -> Dict[str, Any]:
    data = {"status": "ok"}
    return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class CustomerEngagementAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Retrieve all customer engagements.",
        responses={
            200: openapi.Response(
                description="List of customer engagements",
                schema=CustomerEngagementSerializer(many=True)
            )
        }
    )
    def get(self) -> Response:
        engagements = CustomerEngagement.objects.all()
        serializer = CustomerEngagementSerializer(engagements, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        request_body=CustomerEngagementSerializer,
        responses={
            201: openapi.Response(
                description="Customer engagement created successfully",
                schema=CustomerEngagementSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
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
    
    def get_object(self, engagement_id: int) -> Response:
        try:
            return CustomerEngagement.objects.get(id=engagement_id)
        except CustomerEngagement.DoesNotExist:
            raise ValidationError({'error': 'Customer engagement not found'})

    @swagger_auto_schema(
        operation_description="Retrieve a specific customer engagement by ID.",
        responses={
            200: openapi.Response(
                description="Customer engagement details",
                schema=CustomerEngagementSerializer
            ),
            404: openapi.Response(
                description="Customer engagement not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def get(self, request: Request, engagement_id: int) -> Response:
        engagement = self.get_object(engagement_id)
        serializer = CustomerEngagementSerializer(engagement)
        return Response(serializer.data)


    @swagger_auto_schema(
        request_body=CustomerEngagementSerializer,
        responses={
            200: openapi.Response(
                description="Customer engagement updated successfully",
                schema=CustomerEngagementSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Customer engagement not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def put(self, request: Request, engagement_id: int) -> Response:
        engagement = self.get_object(engagement_id)
        serializer = CustomerEngagementSerializer(engagement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        responses={
            204: openapi.Response(
                description="Customer engagement deleted successfully"
            ),
            404: openapi.Response(
                description="Customer engagement not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def delete(self, engagement_id: int) -> Response:
        engagement = self.get_object(engagement_id)
        engagement.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
    
@method_decorator(csrf_exempt, name='dispatch')
class CustomerAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Retrieve all customers.",
        responses={
            200: openapi.Response(
                description="List of customers",
                schema=CustomerSerializer(many=True)
            )
        }
    )
    def get(self) -> Response:
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        request_body=CustomerSerializer,
        responses={
            201: openapi.Response(
                description="Customer created successfully",
                schema=CustomerSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            500: openapi.Response(
                description="Server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
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

    def get_object(self, customer_id: int) -> Customer:
        try:
            return Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError({'error': 'Customer not found'})

    @swagger_auto_schema(
        operation_description="Retrieve a specific customer by ID.",
        responses={
            200: openapi.Response(
                description="Customer details",
                schema=CustomerSerializer
            ),
            404: openapi.Response(
                description="Customer not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def get(self, customer_id: int) -> Response:
        customer = self.get_object(customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


    @swagger_auto_schema(
        request_body=CustomerSerializer,
        responses={
            200: openapi.Response(
                description="Customer updated successfully",
                schema=CustomerSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Customer not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def put(self, request: Request, customer_id: int) -> Response:
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


    @swagger_auto_schema(
        operation_description="Delete a customer by ID.",
        responses={
            204: openapi.Response(
                description="Customer deleted successfully"
            ),
            404: openapi.Response(
                description="Customer not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def delete(self, customer_id: int) -> Response:
        try:
            customer = self.get_object(customer_id)
            customer.delete()
            return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            logger.error(f"Error deleting customer: {str(e)}")
            return Response({'error': 'Failed to delete customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_customer_exists(first_name: str, last_name: str, phone_number: int, country_code: int, email: str) -> Dict[str, Any]:
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

    @swagger_auto_schema(
        operation_description="Retrieve all knowledge base embeddings.",
        responses={
            200: openapi.Response(
                description="List of embeddings",
                schema=KbEmbeddingSerializer(many=True)
            )
        }
    )
    def get(self) -> Response:
        embeddings = KbEmbedding.objects.all()
        serializer = KbEmbeddingSerializer(embeddings, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="Create a new knowledge base embedding.",
        request_body=KbEmbeddingSerializer,
        responses={
            201: openapi.Response(
                description="Embedding created successfully",
                schema=KbEmbeddingSerializer
            ),
            400: openapi.Response(
                description="Invalid data provided",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
        serializer = KbEmbeddingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class KbEmbeddingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, embedding_id: int) -> KbEmbedding:
        try:
            return KbEmbedding.objects.get(id=embedding_id)
        except KbEmbedding.DoesNotExist:
            raise ValidationError({'error': 'Embedding not found'})


    @swagger_auto_schema(
        operation_description="Retrieve a knowledge base embedding by ID.",
        responses={
            200: openapi.Response(
                description="Embedding details",
                schema=KbEmbeddingSerializer
            ),
            404: openapi.Response(
                description="Embedding not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        embedding_id = kwargs.get('embedding_id')
        embedding = self.get_object(embedding_id)
        
        serializer = KbEmbeddingSerializer(embedding)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="Update a knowledge base embedding by ID.",
        request_body=KbEmbeddingSerializer,
        responses={
            200: openapi.Response(
                description="Embedding updated successfully",
                schema=KbEmbeddingSerializer
            ),
            400: openapi.Response(
                description="Invalid data provided",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Embedding not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def put(self, request: Request, *args, **kwargs) -> Response:
        embedding_id = kwargs.get('embedding_id')
        embedding = self.get_object(embedding_id)
        serializer = KbEmbeddingSerializer(embedding, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_description="Delete a knowledge base embedding by ID.",
        responses={
            204: openapi.Response(
                description="Embedding deleted successfully"
            ),
            404: openapi.Response(
                description="Embedding not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        embedding_id = kwargs.get('embedding_id')
        embedding = self.get_object(embedding_id)
        embedding.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)