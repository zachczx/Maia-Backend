from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from core.utils.openai_utils import get_openai_llm_client
import logging
import json

load_dotenv()
logger = logging.getLogger('django')

def do_speaker_diarization(transcript):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Given the transcription of a conversation between a customer service representative (CSO) and a caller, perform speaker diarization such that the content spoken by each speaker is delimited by `|`. You may assume that the CSO will always speak first. Use the content from transcript only, do not add extra content. The transcript given may not be complete, do not try to complete it.
                
                Example response:
                Hi! How can I help you? | I would like to ask some questions about NS Pay. | Sure, What question do you have?
                
                If there is no transcript given, return an empty string.
                """,
            ),
            ("human", "TRANSCRIPT: {transcript}"),
        ]
    )
    
    llm = get_openai_llm_client()
    chain = prompt | llm
    
    response = chain.invoke(
        {
            "transcript": transcript,
        }
    )
    
    transcript_with_speakers = response.content
    logger.info("Speaker diarization completed by OpenAI")
    return transcript_with_speakers
