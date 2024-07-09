from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QueryRequest:
    case_information: str
    response_format: Optional[str] = None
    response_template: Optional[str] = None
    domain_knowledge: Optional[str] = None
    past_responses: Optional[str] = None
    extra_information: Optional[str] = None
    history: Optional[List[List[str]]] = None

@dataclass
class QueryResponse:
    case_title: str
    case_type: str
    case_description: str
    priority: str
    category: str
    sub_category: str
    sub_subcategory: str
    sentiment: str
    suggested_reply: str
    log: list
    

