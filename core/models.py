from django.db import models
from django.contrib.auth.models import User
from django.db import models

class KbResource(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, blank = True, null=True)
    sub_category = models.CharField(max_length=255, blank = True, null=True)
    sub_subcategory = models.CharField(max_length=255, blank = True, null=True)
    tag = models.CharField(max_length=255, blank = True, null=True)
    status = models.IntegerField(blank = True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    
    class Meta:
        db_table = 'kb_resource'
    
    def __str__(self):
        return str(self.id)

class KbEmbedding(models.Model):
    kb_resource = models.ForeignKey(KbResource, on_delete=models.CASCADE)
    content = models.TextField()
    vector_db_id = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'kb_embedding'
    
    def __str__(self):
        return str(self.id)

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=50)
    email = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    analytics = models.JSONField(blank=True, null=True) # engagement_num, preferred_channel, resolution_status, summary, past aggression

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return f'Customer {self.id}'

class CustomerEngagement(models.Model):
    customer  = models.ForeignKey(Customer, on_delete=models.CASCADE, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    channel = models.IntegerField() # 0 - call, 1 - web chat, 2 email
    query_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    sub_subcategory = models.CharField(max_length=100, blank=True, null=True)
    root_cause = models.CharField(max_length=255)
    sentiment = models.CharField(max_length=20)
    suggested_reply = models.TextField(blank=True, null=True)
    conversation = models.TextField(blank=True, null=True)
    call_duration = models.DurationField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    resolution = models.BooleanField(default=False)
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'customer_engagement'

    def __str__(self):
        return f'CustomerEngagement {self.id} - {self.timestamp}'
