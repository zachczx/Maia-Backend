from dataclasses import dataclass

@dataclass
class KbResource():
    id: int
    name: str
    category: str
    sub_category: str
    sub_subcategory: str
    tag: str
    
    def get_metadata(self) -> str:
        metadata = []
        if self.category !=None:
            metadata.append(self.category)
            
        if self.sub_category !=None:
            metadata.append(self.sub_category)
            
        if self.sub_subcategory !=None:
            metadata.append(self.sub_subcategory)

        return f"[{','.join(metadata)}]"


@dataclass
class TextChunk():
    content: str
    