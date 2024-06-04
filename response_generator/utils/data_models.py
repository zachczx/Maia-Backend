from dataclasses import dataclass

@dataclass
class KbResource():
    id: int
    category: str
    sub_category: str
    tag: str
    status: int
    
    def get_metadata(self) -> str:
        return f"[{self.category},{self.sub_category}] "

class KbEmbedding():
    id: int
    kb_resource_id: int
    content: str
    vector_db_id: int