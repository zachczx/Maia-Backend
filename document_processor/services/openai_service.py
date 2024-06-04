from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def get_openai_embedding_client():
    return OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

def get_embedding(content, embedding_client):   
    embedding = embedding_client.embed_query(content)
    return embedding