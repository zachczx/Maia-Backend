from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def get_openai_embedding_client():
    return OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

def get_embedding(text_chunk, embedding_client):
    embedding = embedding_client.embed_query(text_chunk)
    return embedding