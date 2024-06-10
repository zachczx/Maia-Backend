from .openai_service import get_llm_response
from core.utils.opensearch import search_vector_db
import logging

logger = logging.getLogger('django')


def chat(chat_history):
    query = chat_history[-1]['content']
    
    contexts = search_vector_db(query)

    if len(contexts) > 0:
        response = get_llm_response(query, contexts, chat_history)
    else:
        response = "I'm sorry, but I don't have the information on that topic right now."
    return response
