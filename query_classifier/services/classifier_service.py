from .openai_service import get_query_summary
from core.utils.opensearch_utils import search_vector_db
from .openai_service import get_classifier_completions
import logging

logger = logging.getLogger('django')

def query_classifier(query_data):
    # send query to get summarised
    if query_data.history != None or query_data.history!=[]:
        query_list = get_query_summary(query_data.case_information)
    
        # get relevant context for each question
        contexts = {}
        for summarised_query in query_list:
            context = search_vector_db(summarised_query)
            contexts[summarised_query] = context
        
    # send context + query + chat history to get classified + response
    query_response = get_classifier_completions(query_data, contexts)
    
    return query_response