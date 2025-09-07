from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid

class MCPPayload(BaseModel):
    retrieved_context: List[Dict[str, Any]]
    query: str

class MCPMessage(BaseModel):
    sender: str
    receiver: str
    type: str = "CONTEXT_RESPONSE"
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: MCPPayload