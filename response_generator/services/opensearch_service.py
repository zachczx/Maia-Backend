from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth


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
    return opensearch_client


def get_opensearch_endpoint(domain_name, region):
    client = boto3.client('es', region_name=region)
    response = client.describe_elasticsearch_domain(
        DomainName=domain_name
    )
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
    return bool(response['acknowledged'])


def create_index_mapping(opensearch_client, index_name):
    response = opensearch_client.indices.put_mapping(
        index=index_name,
        body={
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1536
                }
            }
        }
    )
    return bool(response['acknowledged'])


def add_document(opensearch_client, index_name, embedding):
    document_data = {
        "embedding": embedding
    }
    response = opensearch_client.index(index=index_name, body=document_data)
    
    return response['_id']


client = get_opensearch_cluster_client("vector-kb","ap-southeast-1")
print(check_opensearch_index(client, "vector-kb-index"))