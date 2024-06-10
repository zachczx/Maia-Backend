from rest_framework import serializers

class QueryClassifierSerializer(serializers.Serializer):
    query = serializers.CharField()
    history = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        required=False
    )