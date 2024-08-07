from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .services.chat_service import chat
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
import logging

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class ResponseGeneratorView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Generate a response based on chat history.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'chat_history': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="List of chat messages"
                )
            },
            required=['chat_history']
        ),
        responses={
            200: openapi.Response(
                description="Generated response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'response': openapi.Schema(type=openapi.TYPE_STRING, description='Chatbot response')
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'response': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            response = chat(data["chat_history"], False)
            
            return Response({'response': response}, status=status.HTTP_200_OK)
        except:
            return Response({'response': 'An error has occurred.'}, status=status.HTTP_400_BAD_REQUEST)