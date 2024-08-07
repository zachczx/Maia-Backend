from rest_framework import serializers

class CustomerProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    country_code = serializers.CharField(max_length=5)
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField()
