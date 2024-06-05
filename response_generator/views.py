from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import ResponseGeneratorSerialiser
from .services.chat_service import chat

import logging

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class ResponseGeneratorView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResponseGeneratorSerialiser(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            
            response = chat(query)
            
            return Response({'response': response}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)