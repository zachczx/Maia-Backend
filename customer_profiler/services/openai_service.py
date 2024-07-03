from dotenv import load_dotenv
from core.utils.openai_utils import get_openai_llm_client, get_openai_moderation_client
from ..utils.data_models import LLMResponse
import logging
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
logger = logging.getLogger("django")

def get_llm_response(summaries, notes):
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
            You will be given a list of past engagements with a particular customer. Based on the past engagements provided, do the following steps:
            1. Come up with a short summary of the customer, including what they usually call for and the contents of the past engagements. Use only the provided data and do not add information.
            2. Check if there has been aggression shown by the customer towards the call center agent. Return the answer in boolean `true` or `false`.
            
            Return your responses in a json format. This is an example of a correct format:
            {{
                "summary": <summary>,
                "past_aggression": <past aggression>,
            }}
            {input}
        """),
        ("human", "PAST_ENGAGEMENTS: {input}"),
    ])

    past_engagements = ""

    for i in range(len(summaries)):
        summary = summaries[i]
        note = notes[i]
        past_engagements += f"Customer Engagement {i+1}: {summary}, {note}\n"

    llm = get_openai_llm_client().with_structured_output(LLMResponse, method="json_mode")
    chain = prompt_template | llm

    json_response = chain.invoke({
        "input": past_engagements,
    })
    
    logger.info("User profiling completed by OpenAI")
    
    return LLMResponse(json_response["summary"], json_response["past_aggression"])
