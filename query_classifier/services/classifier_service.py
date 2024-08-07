from .openai_service import get_query_summary
from core.utils.opensearch_utils import search_vector_db
from .openai_service import get_classifier_completions
from .redact_service import redact_text
from ..utils.data_models import QueryRequest, QueryResponse
import logging

logger = logging.getLogger('django')

def query_classifier(query_data: QueryRequest) -> QueryResponse:
    query_data.case_information = redact_text(query_data.case_information)
    
    if query_data.history != None or query_data.history!=[]:
        query_list = get_query_summary(query_data.case_information)
    
        contexts = {}
        for summarised_query in query_list:
            context = search_vector_db(summarised_query)
            contexts[summarised_query] = context
        
    query_response = get_classifier_completions(query_data, contexts)
    
    return query_response