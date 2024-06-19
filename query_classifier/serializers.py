from rest_framework import serializers

class TextQueryClassifierSerializer(serializers.Serializer):
    query = serializers.CharField()
    history = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False
    )

class AudioQueryClassifierSerializer(serializers.Serializer):
    query = serializers.FileField()