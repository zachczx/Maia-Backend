from dataclasses import dataclass

@dataclass
class QueryResponse():
    query: str
    query_type: str
    category: str
    sub_category: str
    root_cause: str
    sentiment: str
    suggested_reply: str
    log: list
    

