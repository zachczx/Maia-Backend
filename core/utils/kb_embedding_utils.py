from core.models import KbEmbedding
from core.serializers import KbEmbeddingSerializer
from rest_framework.exceptions import ValidationError
from typing import List, Dict, Any

def get_all_kb_embeddings() -> List[Dict[str, Any]]:
    embeddings = KbEmbedding.objects.all()
    serializer = KbEmbeddingSerializer(embeddings, many=True)
    return serializer.data

def create_kb_embedding(data: Dict[str, Any]) -> Dict[str, Any]:
    serializer = KbEmbeddingSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        raise ValidationError(serializer.errors)

def get_kb_embedding_by_id(embedding_id: int) -> Dict[str, Any]:
    try:
        embedding = KbEmbedding.objects.get(id=embedding_id)
        serializer = KbEmbeddingSerializer(embedding)
        return serializer.data
    except KbEmbedding.DoesNotExist:
        raise ValidationError({'error': 'Embedding not found'})

def update_kb_embedding(embedding_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        embedding = KbEmbedding.objects.get(id=embedding_id)
        serializer = KbEmbeddingSerializer(embedding, data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise ValidationError(serializer.errors)
    except KbEmbedding.DoesNotExist:
        raise ValidationError({'error': 'Embedding not found'})

def delete_kb_embedding(embedding_id: int) -> Dict[str, Any]:
    try:
        embedding = KbEmbedding.objects.get(id=embedding_id)
        embedding.delete()
        return {'status': 'deleted'}
    except KbEmbedding.DoesNotExist:
        raise ValidationError({'error': 'Embedding not found'})
    
def delete_kb_embedding_by_resource_id(resource_id: int) -> Dict[str, Any]:
    try:
        embeddings = KbEmbedding.objects.filter(kb_resource=resource_id)
        if not embeddings.exists():
            raise ValidationError({'error': 'Embedding not found'})
        
        embeddings_count = embeddings.count()
        embeddings.delete()
        
        return {'status': 'deleted', 'count': embeddings_count}
    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError({'error': str(e)})