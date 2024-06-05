from .openai_service import get_embedding, get_openai_embedding_client, get_llm_response
from langchain_community.vectorstores import OpenSearchVectorSearch
from .opensearch_service import get_opensearch_endpoint
from requests_aws4auth import AWS4Auth
from opensearchpy import RequestsHttpConnection
import logging
import boto3

logger = logging.getLogger('django')

def chat(chat_history, _is_aoss=False):
    query = chat_history[-1]['content']
    
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

    if len(contexts) > 0:
        response = get_llm_response(query, contexts, chat_history)
    else:
        response = "I'm sorry, but I don't have the information on that topic right now."
    return response
