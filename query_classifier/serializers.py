from rest_framework import serializers
from django.core.exceptions import ValidationError
import os

class TextQueryClassifierSerializer(serializers.Serializer):
    case_information = serializers.CharField()
    response_format = serializers.CharField(required=False)
    response_template = serializers.CharField(required=False)
    domain_knowledge = serializers.CharField(required=False)
    past_responses = serializers.CharField(required=False)
    extra_information = serializers.CharField(required=False)
    history = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False
    )

class AudioQueryClassifierSerializer(serializers.Serializer):
    case_information = serializers.FileField()
    response_format = serializers.CharField(required=False)
    response_template = serializers.CharField(required=False)
    domain_knowledge = serializers.CharField(required=False)
    past_responses = serializers.CharField(required=False)
    extra_information = serializers.CharField(required=False)   

class CategoryExcelProcessorSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1]  # Get file extension
        valid_extensions = ['.xls', '.xlsx']
        if ext.lower() not in valid_extensions:
            raise ValidationError("File is not in Excel format.")
        return value