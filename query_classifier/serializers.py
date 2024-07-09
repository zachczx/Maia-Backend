from rest_framework import serializers
from django.core.exceptions import ValidationError
import os

class TextQueryClassifierSerializer(serializers.Serializer):
    query = serializers.CharField()
    notes = serializers.CharField()
    history = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False
    )

class AudioQueryClassifierSerializer(serializers.Serializer):
    query = serializers.FileField()
    notes = serializers.CharField()    

class CategoryExcelProcessorSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1]  # Get file extension
        valid_extensions = ['.xls', '.xlsx']
        if ext.lower() not in valid_extensions:
            raise ValidationError("File is not in Excel format.")
        return value