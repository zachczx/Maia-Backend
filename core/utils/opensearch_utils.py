from core.utils.openai_utils import get_openai_embedding_client
from langchain_community.vectorstores import OpenSearchVectorSearch
from requests_aws4auth import AWS4Auth
from opensearchpy import RequestsHttpConnection
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import logging

logger = logging.getLogger('django')

def get_opensearch_cluster_client(domain_name, region):
    # Retrieve AWS credentials from the environment or AWS configuration
    session = boto3.Session()
    credentials = session.get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)

    opensearch_endpoint = get_opensearch_endpoint(domain_name, region)

    opensearch_client = OpenSearch(
        hosts=[{'host': opensearch_endpoint, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )
    
    logger.info("Opensearch cluster client initialised")
    return opensearch_client


def get_opensearch_endpoint(domain_name, region):
    client = boto3.client('es', region_name=region)
    response = client.describe_elasticsearch_domain(
        DomainName=domain_name
    )
    logger.info("Openseach endpoint retrieved")
    return response['DomainStatus']['Endpoint']


def check_opensearch_index(opensearch_client, index_name):
    return opensearch_client.indices.exists(index=index_name)


def create_index(opensearch_client, index_name):
    settings = {
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil"
                }
            }
        }
    response = opensearch_client.indices.create(index=index_name, body=settings)
    logger.info("Opensearch index created")
    return bool(response['acknowledged'])


def create_index_mapping(opensearch_client, index_name):
    response = opensearch_client.indices.put_mapping(
        index=index_name,
        body={
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1536
                },
                "content": {
                    "type": "keyword"
                }
            }
        }
    )
    logger.info("Opensearch index mapping created")
    return bool(response['acknowledged'])


def add_document(opensearch_client, index_name, embedding, content):
    document_data = {
        "embedding": embedding,
        "content": content
    }
    response = opensearch_client.index(index=index_name, body=document_data)
    logger.info("Document added to opensearch")
    return response['_id']


def delete_opensearch_index(opensearch_client, index_name):
    logger.info(f"Trying to delete index {index_name}")
    try:
        response = opensearch_client.indices.delete(index=index_name)
        logger.info(f"Index {index_name} deleted")
        return response['acknowledged']
    except Exception as e:
        logger.info(f"Index {index_name} not found, nothing to delete")
        return True


def search_vector_db(query, _is_aoss=False):
    session = boto3.Session()
    credentials = session.get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "ap-southeast-1", 'es', session_token=credentials.token)

    opensearch_endpoint = get_opensearch_endpoint("vector-kb", "ap-southeast-1")

    docsearch = OpenSearchVectorSearch(
        index_name="vector-kb-index",
        embedding_function=get_openai_embedding_client(),
        opensearch_url=f"https://{opensearch_endpoint}",
        http_auth=aws_auth,
        timeout=30,
        is_aoss=_is_aoss,
        connection_class=RequestsHttpConnection,
        use_ssl=True,
        verify_certs=True,
    )

    docs = docsearch.similarity_search_with_score(
        query,
        search_type="script_scoring",
        space_type="cosinesimil",
        vector_field="embedding",
        text_field="content",
        score_threshold=1.5
    )

    contexts = []
    for doc in docs:
        contexts.append(doc[0].page_content)
    logger.info("Similar documents retrieved from Opensearch for context")
    return contexts