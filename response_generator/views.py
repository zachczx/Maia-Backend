from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .services.chat_service import chat
import json

import logging

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class ResponseGeneratorView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            response = chat(data["chat_history"])
            
            return Response({'response': response}, status=status.HTTP_200_OK)
        except:
            return Response({'response': 'An error has occurred.'}, status=status.HTTP_400_BAD_REQUEST)