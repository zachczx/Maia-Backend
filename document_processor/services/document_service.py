from .openai_service import get_embedding, get_openai_embedding_client
from .opensearch_service import add_document, get_opensearch_cluster_client, delete_opensearch_index, create_index, create_index_mapping
from core.utils import kb_embedding_service, kb_resource_service
from ..utils.data_models import TextChunk
from pathlib import Path
from openpyxl import load_workbook
import os
import logging
import time

logger = logging.getLogger('django')


def process_document(file_path, kb_resource):

    file_extension = Path(file_path).suffix
    
    match file_extension:
        case ".pdf":
            text_chunks = read_pdf(file_path)
        case ".xlsx":
            text_chunks = read_excel(file_path)
        case _:
            logger.error("File type is not supported")
            return

    metadata = kb_resource.get_metadata()
    
    kb_resource_id = add_kb_resource(kb_resource=kb_resource)
    
    if kb_resource_id != 0:
        add_chunks(text_chunks, metadata, kb_resource_id)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("File deleted successfully")
    
    return


def add_kb_resource(kb_resource):
    data = {
        "status": 1
    }

    if kb_resource.category !=None and kb_resource.category !="":
        data["category"] = kb_resource.category
        
    if kb_resource.sub_category !=None and kb_resource.sub_category !="":
        data["sub_category"] = kb_resource.sub_category
        
    if kb_resource.tag !=None and kb_resource.tag !="":
        data["tag"] = kb_resource.tag
    
    try:
        kb_resource_row = kb_resource_service.create_kb_resource(data)
        kb_resource_id = kb_resource_row["id"]
        logger.info("Kb_resource added successfully to Postgres DB")
        return kb_resource_id
    except:
        logger.error("Error encountered when adding to kb_resource table")
        return 0


def read_pdf(file_path):
    return # List of List of TextChunk


def read_excel(file_path):
    workbook = load_workbook(filename=file_path, read_only=True)
    text_chunks = []
    
    try:
        for sheet in workbook.worksheets:
            sheet_content = []
            for row in sheet.rows:
                question = row[0].value
                answer = row[1].value
                
                if question == None or answer == None:
                    break
                
                content = question + " " + answer
                text_chunk = TextChunk(content)
                sheet_content.append(text_chunk)
                
            text_chunks.append(sheet_content)
    finally:
        workbook.close()
        logger.info("Excel document processed successfully")
        time.sleep(5)
            
    return text_chunks


def add_chunks(text_chunks, metadata, kb_resource_id):
    opensearch_client = get_opensearch_cluster_client("vector-kb", "ap-southeast-1")
    openai_client = get_openai_embedding_client()
    
    for page in text_chunks:
        for text_chunk in page:
            add_chunk(text_chunk, opensearch_client, openai_client, metadata, kb_resource_id)
    return


def add_chunk(text_chunk, opensearch_client, openai_client, metadata, kb_resource_id):
    embedding = get_embedding(f'{metadata} {text_chunk.content}', openai_client)
    
    # Add to opensearch
    opensearch_id = add_document(opensearch_client, "vector-kb-index", embedding)
    logger.info(opensearch_id)
    
    # Add to postgres
    data = {
        "kb_resource": kb_resource_id,
        "content": text_chunk.content,
        "vector_db_id": opensearch_id,
    }
    kb_embedding_row = kb_embedding_service.create_kb_embedding(data)
    logger.info(f'Kb_embedding {kb_embedding_row["id"]} added successfully to Postgres DB')
    return