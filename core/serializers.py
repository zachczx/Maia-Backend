from rest_framework import serializers
from .models import KbResource, KbEmbedding
from django.contrib.auth.models import User

class KbResourceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    category = serializers.CharField(max_length=255, required=False)
    sub_category = serializers.CharField(max_length=255, required=False)
    tag = serializers.CharField(max_length=255, required=False)
    status = serializers.IntegerField(required=False)
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = KbResource
        fields = ['id', 'created_at', 'updated_at', 'category', 'sub_category', 'tag', 'status']

class KbEmbeddingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    kb_resource = serializers.PrimaryKeyRelatedField(queryset=KbResource.objects.all())
    content = serializers.CharField()
    vector_db_id = serializers.CharField(max_length=255)
    
    class Meta:
        model = KbEmbedding
        fields = ['id', 'kb_resource', 'content', 'vector_db_id']
