from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from ..utils.data_models import QueryResponse
from core.utils.openai_utils import get_openai_llm_client
import logging
import json
import re
import csv
import os

load_dotenv()
logger = logging.getLogger('django')

def read_csv_file(file_type): # file_type = website or category
    file_name = ''
    
    if file_type == "website":
        file_name = 'websites_kb.csv'
    elif file_type == "category":
        file_name = 'categories.csv'
        
    values = []
    csv_file_path = os.path.join('query_classifier', 'config', file_name)
    
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            values.append(row[0])
    
    return values

def read_prompt_file():
    prompt_file_path = os.path.join('query_classifier', 'config', 'prompt.txt')

    try:
        with open(prompt_file_path, 'r') as file:
            chunk_of_text = file.read()
            return chunk_of_text
    except FileNotFoundError:
        return None

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
    sub_subcategory = openai_response.get("sub_subcategory", None)
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
        sub_subcategory=sub_subcategory,
        root_cause=root_cause,
        sentiment=sentiment,
        suggested_reply=suggested_reply,
        log=messages
    )


def get_classifier_completions(query, history, context=None):
    delimiter = "####"
    websites = read_csv_file("website")
    categories = read_csv_file("category")
    system_message = read_prompt_file()
    
    # replace values in prompt
    system_message = system_message.replace("{delimiter}", delimiter)
    system_message = system_message.replace("{websites}", ", ".join(websites))
    system_message = system_message.replace("{categories}", "\n".join(categories))
    
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