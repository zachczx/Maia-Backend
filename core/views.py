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