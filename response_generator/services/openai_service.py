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
                """
                You are a helpful assistant that generates a short and concise answer for the customer query (less than 50 words) based on the CONTEXT. The CONTEXT given is retrieved from a knowledge base with FAQs and relevant documents regarding MINDEF. Do not use other information outside of the CONTEXT given. Consider the chat history when determining CONTEXT and generating answer. Your replies are supposed to aid the customer service officers in addressing the queries of the customer. 
                
                If CALL_ASSISTANT is set to False, phrase the response as concise and clear instruction/information which will be used by the CSO to answer the customer query.
                
                If CALL_ASSISTANT is True, phrase the response as though you are the CSO replying to the caller 
                If CALL_ASSISTANT is True and there is no given CONTEXT, respond with a follow-up question or inform the customer service officer that you don't have an answer at the moment. 
                
                This should taken into account MINDEF-specific contextual cues such as acronyms and keywords, such as but not limited to: 
                * "NS" refers to national service. 
                * "MINDEF" refers to Ministry of Defence.
                * "PE" refers to pre-enlistee.
                * "SAFVC" refers to the Singapore Armed Forces Volunteer Corp.
                * "NSF" refers to full-time National Serviceman.
                * "NSman" refers to Operationally Ready National Serviceman.
                * "OneNS" refers to eservices and anything regarding the ns portal. 
                * "HSP/FFI" refers to the SAF Health Screening Programme (hsp) and ffi refers to "Fitness for Instruction" - a medical examination done before certain courses or deployments which are deemed to require medical clearance before participation.
                * “DOE” refers to date of enlistment. 
                * “FRO” refers to further reporting order. 
                * “FME” refers to full medical examination. 
                * “PES” refers to physical employment standard.
                * “LOI” refers to letter of identity.
                """,
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