from django.db import models
# from django.contrib.auth.models import User

class KbResource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, blank = True, null=True)
    sub_category = models.CharField(max_length=255, blank = True, null=True)
    tag = models.CharField(max_length=255, blank = True, null=True)
    status = models.IntegerField(blank = True, null=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, blank = True)
    
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


