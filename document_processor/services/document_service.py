from core.utils.openai_utils import get_embedding, get_openai_embedding_client
from core.utils.opensearch_utils import add_document, get_opensearch_cluster_client, delete_opensearch_index, create_index, create_index_mapping
from core.utils import kb_embedding_utils, kb_resource_utils
from ..utils.data_models import TextChunk
from pathlib import Path
from openpyxl import load_workbook
import os
import logging
import time

logger = logging.getLogger('django')


def process_document(file_path, kb_resource):
    # client = get_opensearch_cluster_client("vector-kb", "ap-southeast-1")
    # delete_opensearch_index(client, "vector-kb-index")
    # create_index(client, "vector-kb-index")
    # create_index_mapping(client, "vector-kb-index")

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
    return # List of List of TextChunk


def read_excel(file_path):
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


def add_chunks(text_chunks, metadata, kb_resource_id):
    opensearch_client = get_opensearch_cluster_client("vector-kb", "ap-southeast-1")
    openai_client = get_openai_embedding_client()
    
    for page in text_chunks:
        for text_chunk in page:
            add_chunk(text_chunk, opensearch_client, openai_client, metadata, kb_resource_id)
    return


def add_chunk(text_chunk, opensearch_client, openai_client, metadata, kb_resource_id):
    embedding = get_embedding(f'{metadata} {text_chunk.content}', openai_client)
    
    # Add to postgres
    data = {
        "kb_resource": kb_resource_id,
        "content": text_chunk.content,
    }
    kb_embedding_row = kb_embedding_utils.create_kb_embedding(data)
    logger.info(f'Kb_embedding {kb_embedding_row["id"]} added successfully to Postgres DB')
    
    # Add to opensearch
    opensearch_id = add_document(opensearch_client, "vector-kb-index", embedding, text_chunk.content, kb_embedding_row["id"])

    return