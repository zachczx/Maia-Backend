from django.contrib import admin
from .models import KbResource, KbEmbedding, CustomerEngagement

admin.site.register(KbResource)
admin.site.register(KbEmbedding)
admin.site.register(CustomerEngagement)
