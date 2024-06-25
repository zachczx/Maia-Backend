from core.models import CustomerEngagement
from core.serializers import CustomerEngagementSerializer
from rest_framework.exceptions import ValidationError

def get_all_customer_engagements():
    engagements = CustomerEngagement.objects.all()
    serializer = CustomerEngagementSerializer(engagements, many=True)
    return serializer.data

def get_customer_engagement_by_id(engagement_id):
    try:
        engagement = CustomerEngagement.objects.get(id=engagement_id)
        serializer = CustomerEngagementSerializer(engagement)
        return serializer.data
    except CustomerEngagement.DoesNotExist:
        raise ValidationError({'error': 'Customer engagement not found'})

def create_customer_engagement(data):
    serializer = CustomerEngagementSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        raise ValidationError(serializer.errors)

def update_customer_engagement(engagement_id, data):
    try:
        engagement = CustomerEngagement.objects.get(id=engagement_id)
        serializer = CustomerEngagementSerializer(engagement, data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise ValidationError(serializer.errors)
    except CustomerEngagement.DoesNotExist:
        raise ValidationError({'error': 'Customer engagement not found'})

def delete_customer_engagement(engagement_id):
    try:
        engagement = CustomerEngagement.objects.get(id=engagement_id)
        engagement.delete()
        return {'status': 'deleted'}
    except CustomerEngagement.DoesNotExist:
        raise ValidationError({'error': 'Customer engagement not found'})
