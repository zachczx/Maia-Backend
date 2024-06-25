from .openai_service import get_llm_response, get_query
from core.utils.opensearch_utils import search_vector_db
import logging

logger = logging.getLogger('django')


def chat(chat_history, call_assistant):
    if call_assistant:
        query = get_query(chat_history)
    else:
        query = chat_history[-1]['content']
    
    contexts = search_vector_db(query)

    if len(contexts) == 0 and not call_assistant:
        response = "I'm sorry, but I don't have the information on that topic right now."
        
    if len(contexts) > 0 or call_assistant:
        response = get_llm_response(query, contexts, chat_history, call_assistant)
    
    return response
