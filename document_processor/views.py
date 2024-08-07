from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import FileUploadSerializer
from .utils.data_models import KbResource
from .services.document_service import process_document
from .services.delete_service import delete_resource
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.files.uploadedfile import UploadedFile
from core.utils import (
    kb_embedding_utils,
    kb_resource_utils
)
import os
import uuid
import logging

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Upload a file and process it.",
        request_body=FileUploadSerializer,
        responses={
            200: openapi.Response(
                description="File received",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message')
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
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            name = serializer.validated_data.get('name', None)
            category = serializer.validated_data.get('category', None)
            sub_category = serializer.validated_data.get('sub_category', None)
            sub_subcategory = serializer.validated_data.get('sub_subcategory', None)
            tag = serializer.validated_data.get('tag', None)
            file_path = self.save_uploaded_file(file)
            
            if name == None:
                name = file.name.split('.')[0]
            
            kb_resource = KbResource(id=None, name=name, category=category, sub_category=sub_category, sub_subcategory=sub_subcategory, tag=tag)
            process_document(file_path, kb_resource)
            
            return Response({'message': 'File received'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def save_uploaded_file(self, file: UploadedFile) -> str:
        try:
            base_dir = os.path.dirname(os.path.realpath(__file__))
            temp_dir = os.path.join(base_dir, 'temp')
            _, ext = os.path.splitext(file.name)
            os.makedirs(temp_dir, exist_ok=True)
            
            file_name = f"temp_{uuid.uuid4()}{ext}"
            file_path = os.path.join(base_dir, 'temp', file_name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            logger.info("File saved successfully")
            
            return file_path
        except:
            return ""
    
    
    def get_file_name(self, file: UploadedFile) -> str:
        file_name = file.name
        return file_name
        

@method_decorator(csrf_exempt, name='dispatch')
class ResourceView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific KB resource by ID or get all resources if no ID is provided.",
        responses={
            200: openapi.Response(
                description="KB resources data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            404: openapi.Response(
                description="Resource not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def get(self, request, pk=None):
        try:
            if pk:
                data = kb_resource_utils.get_kb_resource_by_id(pk)
            else:
                data = kb_resource_utils.get_all_kb_resources()
            return Response({'data': data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_description="Update a specific KB resource by ID.",
        responses={
            200: openapi.Response(
                description="Updated KB resource data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: openapi.Response(
                description="Resource not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def put(self, request, pk):
        try:
            data = kb_resource_utils.update_kb_resource(pk, request.data)
            return Response(data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_description="Delete a specific KB resource by ID.",
        responses={
            204: openapi.Response(
                description="Resource deleted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                    }
                )
            ),
            404: openapi.Response(
                description="Resource not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def delete(self, request, pk):
        try:
            data = delete_resource(pk)
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)
