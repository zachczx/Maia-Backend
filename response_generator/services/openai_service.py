from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from core.utils.openai_utils import get_openai_llm_client
from langchain_core.prompts import ChatPromptTemplate
import logging
import json

logger = logging.getLogger('django')


def get_llm_response(query, contexts, chat_history, call_assistant):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that generates a short and concise answer (less than 50 words) based on the context. Do not use other information outside of the context given> Consider the chat history when determining context and generating answer. If CALL_ASSISTANT is equal to True, please phrase the response as though it is being spoken by a call center representative addressing the caller's query. If CALL_ASSISTANT is set to True, respond as a call center representative addressing the caller's query. If CALL_ASSISTANT is True and there is no given context, respond with a follow-up question or inform the caller that you don't have an answer at the moment.",
            ),
            ("human", "QUERY: {query}, CONTEXT: {context}, CHAT_HISTORY: {chat_history}, CALL_ASSISTANT: {call_assistant}"),
        ]
    )
    
    if len(contexts) > 0:
        consolidated_context = ""
        count = 1
        
        for context in contexts:
            consolidated_context += f'{count}. {context}'
            count += 1
        
    chat_history_str = json.dumps(chat_history, indent=4)
    
    llm = get_openai_llm_client()
    chain = prompt | llm
    
    response = chain.invoke(
        {
            "query": query,
            "context": consolidated_context if len(contexts) > 0 else "",
            "chat_history": chat_history_str,
            "call_assistant": call_assistant,
        }
    )
    
    return response.content

def get_query(transcript):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You have been given a transcript of a call conversation between a customer and a call center staff. Retrieve the last query from the conversation. The returned query should be under 30 words, focusing on the main question(s).",
            ),
            ("human", "TRANSCRIPT: {transcript}"),
        ]
    )
    
    llm = get_openai_llm_client()
    chain = prompt | llm
    
    transcript_str = json.dumps(transcript, indent=4)
    
    response = chain.invoke(
        {
            "transcript": transcript_str,
        }
    )
    
    query = response.content
    logger.info("Retrieval of query completed by OpenAI")
    return query