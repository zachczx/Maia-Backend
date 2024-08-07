from .openai_service import get_llm_response, get_query_summary
from core.utils.opensearch_utils import search_vector_db
from typing import List, Any, Dict
import logging

logger = logging.getLogger('django')


def chat(chat_history: List[Dict[str, Any]], call_assistant: bool) -> str:
        
    if call_assistant:
        query_list = get_query_summary(chat_history)
        
    else:
        query_text = chat_history[-1]['content']
        query_list = get_query_summary(query_text)
    
    contexts = {}
    for summarised_query in query_list:
        context = search_vector_db(summarised_query)
        contexts[summarised_query] = context

    if len(contexts) == 0 and not call_assistant:
        response = "I'm sorry, but I don't have the information on that topic right now."
        
    if len(contexts) > 0 or call_assistant:
        response = get_llm_response(query_list, contexts, chat_history, call_assistant)
    
    return response
