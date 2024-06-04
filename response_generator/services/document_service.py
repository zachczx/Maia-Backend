from .openai_service import get_embedding
from ..utils import kb_resource, kb_embedding
from .opensearch_service import add_document

def pdf_reader():
    return

def excel_reader():
    return

def add_document(text_chunk, kb_resource_id):
    embedding = get_embedding(text_chunk)
    
    # add to postgres
    kb_embedding.create_kb_embedding()
    
    # add to opensearch
    add_document
    return

print (kb_resource.get_all_kb_resources())