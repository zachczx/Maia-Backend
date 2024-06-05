from rest_framework import serializers

class ResponseGeneratorSerialiser(serializers.Serializer):
    query = serializers.CharField()
    