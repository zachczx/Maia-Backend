from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger('django')
load_dotenv()


def get_openai_embedding_client():
    return OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)


def get_embedding(content, embedding_client):   
    embedding = embedding_client.embed_query(content)
    return embedding


def get_openai_llm_client():
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm


def get_llm_response(query, contexts):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that generates a short and concise answer (less than 50 words) based on the context. Do not use other information outside of the context given",
            ),
            ("human", "QUERY: {query}, CONTEXT: {context}"),
        ]
    )
    
    consolidated_context = ""
    count = 1
    
    for context in contexts:
        consolidated_context += f'{count}. {context}'
        count += 1
    
    llm = get_openai_llm_client()
    chain = prompt | llm
    
    response = chain.invoke(
        {
            "query": query,
            "context": consolidated_context,
        }
    )
    
    return response.content
