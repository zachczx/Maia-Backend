from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import TextQueryClassifierSerializer, AudioQueryClassifierSerializer
from .services.classifier_service import query_classifier
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from dataclasses import asdict
from core.utils.openai_utils import get_transcription
import logging
import tempfile

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class TextQueryClassifierView(APIView):
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

@method_decorator(csrf_exempt, name='dispatch')
class AudioQueryClassifierView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AudioQueryClassifierSerializer(data=request.data)
        if serializer.is_valid():
            audio_query = serializer.validated_data['query']
            
            file_path = self.save_audio_to_wav_file(audio_query)
            text_query = get_transcription(file_path)
            response = query_classifier(text_query, None)
            json_response = asdict(response)
            
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def save_audio_to_wav_file(self, audio_data):
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        file_path = temp_file.name

        with open(file_path, 'wb') as f:
            f.write(audio_data.read())
            
        logger.info("Audio file saved as temporary file")
        return file_path
        