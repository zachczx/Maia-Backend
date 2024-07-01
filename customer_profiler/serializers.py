# serializers.py
from rest_framework import serializers

class CustomerProfileSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
