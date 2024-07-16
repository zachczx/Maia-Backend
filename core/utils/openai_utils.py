from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import OpenAIModerationChain
from openai import OpenAI as BaseOpenAI
import logging


load_dotenv()
logger = logging.getLogger('django')

def get_openai_moderation_client():
    moderate = OpenAIModerationChain()
    logger.info("OpenAI Moderation client initialised")
    return moderate

def moderate_user_message(content):
    moderate = get_openai_moderation_client()

def get_openai_embedding_client():
    logger.info("OpenAI Embedding client initialised")
    return OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

def get_embedding(content, embedding_client):   
    embedding = embedding_client.embed_query(content)
    logger.info("Text converted to embeddings")
    return embedding

def get_openai_llm_client():
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=500,
        timeout=None,
        max_retries=2,
    )
    logger.info("OpenAI LLM client initialised")
    return llm

def get_whisper_client():
    client = BaseOpenAI()
    logger.info("OpenAI Whisper client initialised")
    return client

def get_transcription(file_path, client=get_whisper_client()):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            temperature=0,
            prompt="This audio chunk is part of a conversation between a call center staff and a customer. Do not attempt to complete any cut-off words; transcribe only what is clearly audible.",
            language="en",
            response_format="text"
        )

    # Process transcription 
    text = transcription.replace("...", "")
    logger.info("Audio transcription is completed")
    return text
