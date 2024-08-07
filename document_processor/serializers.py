from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255, required = False)
    sub_category = serializers.CharField(max_length=255, required = False)
    sub_subcategory = serializers.CharField(max_length=255, required = False)
    tag = serializers.CharField(max_length=255, required = False)
    