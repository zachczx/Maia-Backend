from core.utils.openai_utils import get_embedding
from core.utils.opensearch_utils import add_document, get_opensearch_cluster_client, delete_opensearch_index, create_index, create_index_mapping
from core.utils import kb_embedding_utils, kb_resource_utils
from ..utils.data_models import TextChunk, KbResource
from pathlib import Path
from openpyxl import load_workbook
from typing import List
from opensearchpy import OpenSearch
import os
import logging
import time

logger = logging.getLogger('django')


def process_document(file_path: str, kb_resource: KbResource):

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
    
    return None


def add_kb_resource(kb_resource: KbResource) -> int:
    data = {
        "status": 1
    }
    
    if kb_resource.name !=None and kb_resource.name !="":
        data["name"] = kb_resource.name

    if kb_resource.category !=None and kb_resource.category !="":
        data["category"] = kb_resource.category
        
    if kb_resource.sub_category !=None and kb_resource.sub_category !="":
        data["sub_category"] = kb_resource.sub_category
        
    if kb_resource.sub_subcategory !=None and kb_resource.sub_subcategory !="":
        data["sub_subcategory"] = kb_resource.sub_subcategory
        
    if kb_resource.tag !=None and kb_resource.tag !="":
        data["tag"] = kb_resource.tag
        
    
    try:
        kb_resource_row = kb_resource_utils.create_kb_resource(data)
        kb_resource_id = kb_resource_row["id"]
        logger.info("Kb_resource added successfully to Postgres DB")
        return kb_resource_id
    except Exception as e:
        logger.error("Error encountered when adding to kb_resource table: %s", str(e))
        return 0


def read_pdf(file_path):
    return


def read_excel(file_path: str) -> List[List[TextChunk]]:
    workbook = load_workbook(filename=file_path, read_only=True)
    text_chunks = []
    
    try:
        for sheet in workbook.worksheets:
            sheet_content = []
            for row in sheet.rows:
                if len(row) < 2:
                    break
                
                question = row[0].value
                answer = row[1].value
                
                if question == None or answer == None:
                    break
                
                content = question + "\n\n" + answer
                text_chunk = TextChunk(content)
                sheet_content.append(text_chunk)
                
            text_chunks.append(sheet_content)
    finally:
        workbook.close()
        logger.info("Excel document processed successfully")
        time.sleep(5)
            
    return text_chunks


def add_chunks(text_chunks: List[List[TextChunk]], metadata: str, kb_resource_id: int) -> None:
    opensearch_client = get_opensearch_cluster_client("vector-kb", "ap-southeast-1")
    
    for page in text_chunks:
        for text_chunk in page:
            add_chunk(text_chunk, opensearch_client, metadata, kb_resource_id)
    return None


def add_chunk(text_chunk: TextChunk, opensearch_client: OpenSearch, metadata: str, kb_resource_id: int) -> None:
    embedding = get_embedding(f'{metadata} {text_chunk.content}')
    
    data = {
        "kb_resource": kb_resource_id,
        "content": text_chunk.content,
    }
    kb_embedding_row = kb_embedding_utils.create_kb_embedding(data)
    logger.info(f'Kb_embedding {kb_embedding_row["id"]} added successfully to Postgres DB')

    opensearch_id = add_document(opensearch_client, "vector-kb-index", embedding, text_chunk.content, kb_embedding_row["id"])

    return