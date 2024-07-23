from rest_framework import serializers
from .models import KbResource, KbEmbedding, CustomerEngagement, Customer

class KbResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = KbResource
        fields = '__all__'
        
class KbEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = KbEmbedding
        fields = '__all__'
        
class CustomerEngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerEngagement
        fields = '__all__'
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'