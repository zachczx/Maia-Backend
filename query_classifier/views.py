from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import TextQueryClassifierSerializer, AudioQueryClassifierSerializer, CategoryExcelProcessorSerializer
from .services.classifier_service import query_classifier
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from dataclasses import asdict
from core.utils.openai_utils import get_transcription
from .services import category_processing_service
from .utils.data_models import QueryRequest
from rest_framework.permissions import IsAuthenticated
from django.core.files.uploadedfile import UploadedFile
from drf_yasg.utils import swagger_auto_schema
import logging
import tempfile
import os

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class TextQueryClassifierView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Classify a text query.",
        request_body=TextQueryClassifierSerializer,
        responses={
            200: openapi.Response(
                description="Classified query response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'case_title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the case'),
                        'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the case'),
                        'case_description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the case'),
                        'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority of the case'),
                        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category of the case'),
                        'sub_category': openapi.Schema(type=openapi.TYPE_STRING, description='Sub-category of the case'),
                        'sub_subcategory': openapi.Schema(type=openapi.TYPE_STRING, description='Sub-subcategory of the case'),
                        'sentiment': openapi.Schema(type=openapi.TYPE_STRING, description='Sentiment of the case'),
                        'resolution_notes': openapi.Schema(type=openapi.TYPE_STRING, description='Resolution notes of the case'),
                        'suggested_reply': openapi.Schema(type=openapi.TYPE_STRING, description='Suggested reply for the case'),
                        'log': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='Log of actions or events'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = TextQueryClassifierSerializer(data=request.data)
        if serializer.is_valid():
            query_data = QueryRequest(
                case_information=serializer.validated_data.get('case_information', None),
                response_format=serializer.validated_data.get('response_format', None),
                response_template=serializer.validated_data.get('response_template', None),
                domain_knowledge=serializer.validated_data.get('domain_knowledge', None),
                past_responses=serializer.validated_data.get('past_responses', None),
                extra_information=serializer.validated_data.get('extra_information', None),
                history=serializer.validated_data.get('history', None),
            )
            
            if query_data.history:
                query_data.history = [tuple(item) for item in query_data.history]
            
            response = query_classifier(query_data)
            json_response = asdict(response)
            
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class AudioQueryClassifierView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Classify an audio query.",
        request_body=AudioQueryClassifierSerializer,
        responses={
            200: openapi.Response(
                description="Classified query response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'case_title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the case'),
                        'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the case'),
                        'case_description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the case'),
                        'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority of the case'),
                        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category of the case'),
                        'sub_category': openapi.Schema(type=openapi.TYPE_STRING, description='Sub-category of the case'),
                        'sub_subcategory': openapi.Schema(type=openapi.TYPE_STRING, description='Sub-subcategory of the case'),
                        'sentiment': openapi.Schema(type=openapi.TYPE_STRING, description='Sentiment of the case'),
                        'resolution_notes': openapi.Schema(type=openapi.TYPE_STRING, description='Resolution notes of the case'),
                        'suggested_reply': openapi.Schema(type=openapi.TYPE_STRING, description='Suggested reply for the case'),
                        'log': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='Log of actions or events'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = AudioQueryClassifierSerializer(data=request.data)
        if serializer.is_valid():
            audio_query = serializer.validated_data.get('case_information', None)
            response_format=serializer.validated_data.get('response_format', None)
            response_template=serializer.validated_data.get('response_template', None)
            domain_knowledge=serializer.validated_data.get('domain_knowledge', None)
            past_responses=serializer.validated_data.get('past_responses', None)
            extra_information=serializer.validated_data.get('extra_information', None)
            
            file_path = self.save_audio_to_wav_file(audio_query)
            text_query = get_transcription(file_path)
            
            query_data = QueryRequest(
                case_information=text_query,
                response_format=response_format,
                response_template=response_template,
                domain_knowledge=domain_knowledge,
                past_responses=past_responses,
                extra_information=extra_information,
            )
            response = query_classifier(query_data)
            json_response = asdict(response)
            
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def save_audio_to_wav_file(self, audio_data: UploadedFile) -> str:
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        file_path = temp_file.name

        with open(file_path, 'wb', encoding='utf-8') as f:
            f.write(audio_data.read())
            
        logger.info("Audio file saved as temporary file")
        return file_path

class CategoryExcelProcessorView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryExcelProcessorSerializer

    @swagger_auto_schema(
        operation_description="Process an uploaded Excel file.",
        request_body=CategoryExcelProcessorSerializer,
        responses={
            200: openapi.Response(
                description="File processed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'file_path': openapi.Schema(type=openapi.TYPE_STRING, description='Path to the saved file')
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            500: openapi.Response(
                description="Server error during file processing",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            file_path = self.save_uploaded_file(file)
            
            success, message = category_processing_service.process_excel(file_path)
            if success:
                return Response({"message": message, "file_path": file_path}, status=status.HTTP_200_OK)
            else:
                return Response({"error": message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_uploaded_file(self, file: UploadedFile) -> str:
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') 
            file_path = temp_file.name

            for chunk in file.chunks():
                temp_file.write(chunk)

            temp_file.close()

            logger.info("File saved successfully")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return ""