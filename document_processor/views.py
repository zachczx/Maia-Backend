from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .utils.data_models import KbResource
from .services.document_service import process_document
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
            
            kb_resource = KbResource(id=None, category=category, sub_category=sub_category, tag=tag)
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