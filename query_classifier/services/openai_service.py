from langchain_core.prompts import ChatPromptTemplate
from ..utils.data_models import QueryResponse
from core.utils.openai_utils import get_openai_llm_client
import logging
import json
import re
import csv
import os

logger = logging.getLogger('django')

def read_csv_file(file_type): # file_type = website or category
    file_name = ''
    
    if file_type == "website":
        file_name = 'websites_kb.csv'
    elif file_type == "category":
        file_name = 'categories.csv'
        
    values = []
    csv_file_path = os.path.join('query_classifier', 'config', file_name)
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            values.append(row[0])
    
    return values

def read_prompt_file():
    prompt_file_path = os.path.join('query_classifier', 'config', 'prompt.txt')

    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
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
    
    case_title = openai_response.get("case_title", "Unknown")
    case_type = openai_response.get("case_type", "Unknown")
    case_description = openai_response.get("case_description", "Unknown")
    priority = openai_response.get("priority", "Unknown")
    category = openai_response.get("category", "Unknown")
    sub_category = openai_response.get("sub_category", "Unknown")
    sub_subcategory = openai_response.get("sub_subcategory", None)
    sentiment = openai_response.get("sentiment", "Unknown")
    resolution_notes = openai_response.get("resolution_notes", "Unknown")
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
        case_title=case_title,
        case_type=case_type,
        case_description=case_description,
        priority=priority,
        category=category,
        sub_category=sub_category,
        sub_subcategory=sub_subcategory,
        sentiment=sentiment,
        resolution_notes=resolution_notes,
        suggested_reply=suggested_reply,
        log=messages
    )


def get_classifier_completions(query_data, context=None):
    delimiter = "####"
    websites = read_csv_file("website")
    categories = read_csv_file("category")
    system_message = read_prompt_file()
    
    # replace values in prompt
    system_message = system_message.replace("{delimiter}", delimiter)
    system_message = system_message.replace("{websites}", ", ".join(websites))
    system_message = system_message.replace("{categories}", "\n".join(categories))
    
    openai_input = query_data.history if query_data.history else [("system", system_message)]
    
    input_list = ["CASE_INFORMATION: {case_information}"]
    openai_json_call = {"case_information": query_data.case_information}    
    
    if query_data.history:
        input_list.append("HISTORY: {history}")
        openai_json_call["history"] = query_data.history

    else:
        input_list.append("CONTEXT: {context}")
        openai_json_call["system_message"] = system_message
        openai_json_call["context"] = context

    if query_data.response_format:
        input_list.append("RESPONSE_FORMAT: {response_format}")
        openai_json_call["response_format"] = query_data.response_format
        
    if query_data.response_template:
        input_list.append("RESPONSE_TEMPLATE: {response_template}")
        openai_json_call["response_template"] = query_data.response_template
        
    if query_data.domain_knowledge:
        input_list.append("DOMAIN_KNOWLEDGE: {domain_knowledge}")
        openai_json_call["domain_knowledge"] = query_data.domain_knowledge
        
    if query_data.past_responses:
        input_list.append("PAST_RESPONSES: {past_responses}")
        openai_json_call["past_responses"] = query_data.past_responses
    
    if query_data.extra_information:
        input_list.append("EXTRA_INFORMATION: {extra_information}")
        openai_json_call["extra_information"] = query_data.extra_information

    openai_input.append(("user", ", ".join(input_list)))
    
    context = json.dumps(context)
    
    prompt = ChatPromptTemplate.from_messages(openai_input)
    llm = get_openai_llm_client().with_structured_output(QueryResponse, method="json_mode")

    chain = prompt | llm
    
    openai_response = chain.invoke(
        openai_json_call
    )
    query_response = format_openai_response(openai_response, openai_input, context, query_data.case_information)
    
    logger.info("Classification completed by OpenAI")

    return query_response