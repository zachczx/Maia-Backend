from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from ..utils.data_models import QueryResponse
from core.utils.openai_utils import get_openai_llm_client
import logging
import json
import re

load_dotenv()
logger = logging.getLogger('django')


def get_query_summary(query):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Summarize the provided query/queries. Keep each query summary under 30 words, focusing on the main question(s). Separate multiple queries with the '|' delimiter.",
            ),
            ("human", "QUERY: {query}"),
        ]
    )
    
    llm = get_openai_llm_client()
    chain = prompt | llm
    
    response = chain.invoke(
        {
            "query": query,
        }
    )
    
    # format queries
    query_list = response.content.split("|")
    logger.info("Summarisation of queries completed by OpenAI")
    return query_list


def create_openai_input_params(system_message=None, query=None, context=None, history=None):
    return {
        "system_message": system_message,
        "query": query,
        "context": context
    } if system_message else {"query": query, "history" : history}

def escape_characters(conversation):
    unescaped_curly_open = re.compile(r'(?<!{){(?!{)')
    unescaped_curly_close = re.compile(r'(?<!})}(?!})')
    unescaped_quote = re.compile(r'(?<!\\)"')

    for speech in conversation:
        input_string = speech[1]
        escaped_string = unescaped_curly_open.sub('{{', input_string)
        escaped_string = unescaped_curly_close.sub('}}', escaped_string)
        escaped_string = unescaped_quote.sub('\\"', escaped_string)
        speech[1] = escaped_string
        
    return conversation

def format_openai_response(openai_response, messages, context, query):
    
    query_type = openai_response.get("query_type", "Unknown")
    category = openai_response.get("category", "Unknown")
    sub_category = openai_response.get("sub_category", "Unknown")
    root_cause = openai_response.get("root_cause", "Unknown")
    sentiment = openai_response.get("sentiment", "Unknown")
    suggested_reply = openai_response.get("suggested_reply", "Unknown")

    messages = [list(message) for message in messages]
    messages[-1][1] = messages[-1][1].replace("{query}", query)
    if context:
        messages[-1][1] = messages[-1][1].replace("{context}", context)
    else:
        messages[-1][1] = messages[-1][1].replace("{context}", "")
    
    messages.append(["assistant", json.dumps(openai_response)])
    
    messages = escape_characters(messages)
    
    return QueryResponse(
        query=query,
        query_type=query_type,
        category=category,
        sub_category=sub_category,
        root_cause=root_cause,
        sentiment=sentiment,
        suggested_reply=suggested_reply,
        log=messages
    )


def get_classifier_completions(query, history, context=None):
    delimiter = "####"
    websites = ["https://www.cmpb.gov.sg","https://www.ns.gov.sg","https://www.mindef.gov.sg"]
    system_message = """

    You will be provided with customer service queries.
    The customer service query will be delimited with {delimiter} characters.

    Categories: Exit Permit, Make Up Pay, PE Deferment, NS Registration, NS Enlistment, IPPT, NS FIT, PE Medical, eMart

    Exit Permit sub categories:
    Application procedures
    Supporting document
    Extension/Renewal
    Charge/Fine
    Eligibility
    Permit Status
    Amend/Cancel Permit

    Make Up Pay sub categories:
    Claims submission
    Login Issues
    Amend/Cancel Claims
    Payment Quantum/Calculation
    Refund
    Pay Status
    eService Issues
    Supporting document
    Update details
    Appeal claims
    General enquiries

    eMart sub categories:
    Credit amount
    Credit cycle
    Product delivery
    Product type
    Vendor service

    Follow these steps to answer the customer queries.
    The customer query will be delimited with four hashtags,
    i.e. {delimiter}.

    Step 1:{delimiter} decide whether the customer is asking a question about performing a transaction or general enquries on the process.
    Return the answer as 'Transaction' or 'General Enquiries'

    Step 2:{delimiter} analyses the keywords and phrasing to understand the general intent.
    Based on the analysis, categorizes the query into predefined category, sub category, and the root cause on why are they contacting us. You should select the most relevant category and sub category. Explain the root cause in a clear and concise manner.
    
    Step 3:{delimiter} Analyse the sentiment of the customer and return the answer as 'Positive', 'Neutral', 'Negative' only. Do not return any answer beyond the three provided earlier.

    Step 4:{delimiter} Analyze the query and determine which communication channel it belongs to (web chat, phone call, or email) based on the language and characteristics of the query. Use the context given or search the {websites} to formulate a response which should be in a similar format as given in the input. For example, a email should be replied in an email format, phone call should be replied with a point form call notes for the contact staff to contact the customer.
    The response could include a direct answer, a step-by-step guide, or a list of options for the customer.
    You may personalize the answer using the customer's name and details (if given).
    The context given is related to each queries as identified, ensure that you reply to all queries. Do not use information beyond the context or websites provided. If there is no relevant or given context, you may say that you will check and follow up.

    Step 5:{delimiter}: If the input contains previous chat history, it means that the user is not satisfied with the previous response given. Feedback will be given in the user message. Improve on your previous response as shown in the chat history according to the feedback.

    Use the following format as your thought process/agent scratchpad:
    Step 1:{delimiter} <step 1 reasoning>
    Step 2:{delimiter} <step 2 reasoning>
    Step 3:{delimiter} <step 3 reasoning>
    Step 4:{delimiter} <step 4 reasoning>
    Step 5:{delimiter} <step 5 reasoning>
    Response to user:{delimiter} <response to customer>
    Make sure to include {delimiter} to separate every step.
    
    The output should be formatted as a JSON instance that conforms to the JSON schema below.
    
    Here is the output schema:
    {{
        'query_type': '<type>',
        'category': '<category>',
        'sub_category': '<sub_category>',
        'root_cause': '<root_cause>',
        'sentiment': '<sentiment>',
        'suggested_reply': '<reply>'
    }}
    
    As an example, for the above schema, this is a well-formatted instance:
    {{
        'query_type': 'Transaction',
        'category': 'eMart',
        'sub_category': 'Credit amount',
        'root_cause': 'The keywords "enquire on his emart credit" and "do not have enough credits" indicate that the customer is concerned about the credit amount available for making purchases',
        'sentiment': 'Neutral',
        'suggested_reply': '''
            Dear {{Customer\'s Name}},

            Thank you for reaching out regarding your eMart credits. Unfortunately, there is no advance credit top-up system available. However, you can use your remaining credits for the purchase and pay the outstanding amount using cash. Please note that the purchase of the Army No. 4 uniform can only be done using eMart credits.

            If you have any further questions or need assistance, please feel free to contact us.

            Best regards,
            {{Your Name}}
            '''
    }}
    """
    
    system_message = system_message.replace("{delimiter}", delimiter)
    system_message = system_message.replace("{websites}", ", ".join(websites))
    
    openai_input = history if history else [("system", system_message)]
    openai_input.append(("user", "QUERY: {query}" if history else "QUERY: {query}, CONTEXT: {context}"))
    
    context = json.dumps(context)
    
    prompt = ChatPromptTemplate.from_messages(openai_input)
    llm = get_openai_llm_client().with_structured_output(QueryResponse, method="json_mode")

    chain = prompt | llm
    
    if history:
        openai_json_call = create_openai_input_params(query=query)

    else:
        openai_json_call = create_openai_input_params(system_message=system_message, query=query, context=context)

    openai_response = chain.invoke(
        openai_json_call
    )
    query_response = format_openai_response(openai_response, openai_input, context, query)
    
    logger.info("Classification completed by OpenAI")

    return query_response