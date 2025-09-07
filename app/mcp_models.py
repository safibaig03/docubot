from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid

# --- Payload Definition ---
# This class defines the structure of the core data being passed between agents.
# Inheriting from BaseModel gives us automatic data validation and serialization.
class MCPPayload(BaseModel):
    # 'retrieved_context' is a list, where each item is a dictionary containing
    # the 'content' (str) and 'metadata' (dict) of a document chunk.
    retrieved_context: List[Dict[str, Any]]
    
    # The original user query that triggered the retrieval.
    query: str

# --- Main Message Structure ---
# This class defines the "envelope" for all inter-agent communication,
# ensuring every message has a consistent and predictable format.
class MCPMessage(BaseModel):
    # The role of the agent sending the message (e.g., "CoordinatorAgent").
    sender: str
    
    # The role of the agent intended to receive the message (e.g., "LLMResponseAgent").
    receiver: str
    
    # A string to categorize the message type, with a default value.
    type: str = "CONTEXT_RESPONSE"
    
    # A unique identifier for tracing a request as it moves through the system.
    # `default_factory` automatically calls the function (str(uuid.uuid4()))
    # to generate a new unique ID every time a message is created.
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # The actual data payload, which must conform to the MCPPayload structure defined above.
    payload: MCPPayload