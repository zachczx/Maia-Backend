from core.utils import kb_embedding_utils, kb_resource_utils
import logging

logger = logging.getLogger("django")

def delete_resource(kb_resource_id: int) -> bool:
    result = kb_embedding_utils.delete_kb_embedding_by_resource_id(kb_resource_id)
    if result["status"] == "deleted":
        kb_resource_utils.delete_kb_resource(kb_resource_id)
        return True
    return False