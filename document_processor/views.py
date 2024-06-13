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
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            category = serializer.validated_data.get('category', None)
            sub_category = serializer.validated_data.get('sub_category', None)
            tag = serializer.validated_data.get('tag', None)
            file_path = self.save_uploaded_file(file)
            name = file.name.split('.')[0]
            
            kb_resource = KbResource(id=None, name=name, category=category, sub_category=sub_category, tag=tag)
            process_document(file_path, kb_resource)
            
            return Response({'message': 'File received'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def save_uploaded_file(self, file):
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
    
    def get_file_name(self, file):
        file_name = file.name
        return file_name
        
@method_decorator(csrf_exempt, name='dispatch')
class ResourceView(APIView):
    def get(self, request, pk=None):
        try:
            if pk:
                # Get a single kb resource by id
                data = kb_resource_utils.get_kb_resource_by_id(pk)
            else:
                # Get all kb resources
                data = kb_resource_utils.get_all_kb_resources()
            return Response({'data': data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            data = kb_resource_utils.update_kb_resource(pk, request.data)
            return Response(data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            result = kb_resource_utils.delete_kb_resource(pk)
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)
