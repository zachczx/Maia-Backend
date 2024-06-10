from dataclasses import dataclass

@dataclass
class KbResource():
    id: int
    name: str
    category: str
    sub_category: str
    tag: str
    
    def get_metadata(self) -> str:
        return f"[{self.category},{self.sub_category}]"


@dataclass
class TextChunk():
    content: str
    