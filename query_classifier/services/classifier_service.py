from .openai_service import get_query_summary
from core.utils.opensearch_utils import search_vector_db
from .openai_service import get_classifier_completions
import logging

logger = logging.getLogger('django')

def query_classifier(query, chat_history, notes):
    # send query to get summarised
    if chat_history != None or chat_history!=[]:
        query_list = get_query_summary(query)
    
        # get relevant context for each question
        contexts = {}
        for summarised_query in query_list:
            context = search_vector_db(summarised_query)
            logger
            contexts[summarised_query] = context
        
    # send context + query + chat history to get classified + response
    query_response = get_classifier_completions(query, chat_history, contexts, notes)
    
    return query_response