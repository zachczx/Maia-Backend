from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import OpenAIModerationChain
from openai import OpenAI as BaseOpenAI
from typing import Dict, List
from dotenv import load_dotenv
import logging
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger('django')

def get_openai_moderation_client() -> OpenAIModerationChain:
    moderate = OpenAIModerationChain()
    logger.info("OpenAI Moderation client initialised")
    return moderate

def get_openai_embedding_client() -> OpenAIEmbeddings:
    logger.info("OpenAI Embedding client initialised")
    return OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536, api_key=OPENAI_API_KEY)

def get_embedding(content: str, embedding_client: OpenAIEmbeddings = get_openai_embedding_client()) -> List[float]:   
    embedding = embedding_client.embed_query(content)
    logger.info("Text converted to embeddings")
    return embedding

def get_openai_llm_client() -> ChatOpenAI:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=500,
        timeout=None,
        max_retries=2,
        api_key=OPENAI_API_KEY,
    )
    logger.info("OpenAI LLM client initialised")
    return llm

def get_whisper_client() -> BaseOpenAI:
    client = BaseOpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI Whisper client initialised")
    return client

def get_transcription(file_path: str, client: BaseOpenAI = get_whisper_client()) -> str:
    prompt = "This audio chunk is part of a conversation between a call center staff and a customer. Do not attempt to complete any cut-off words; transcribe only what is clearly audible."
    
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            temperature=0,
            prompt=prompt,
            language="en",
            response_format="text"
        )

    transcript = transcription.replace("...", "")
    logger.info("Audio transcription is completed")
    return transcript
