import uuid
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from google.api_core.exceptions import ResourceExhausted

# Import the specialized agents and the MCP data models
from .agents.retrieval_agent import RetrievalAgent
from .agents.ingestion_agent import IngestionAgent
from .agents.llm_response_agent import LLMResponseAgent
from .mcp_models import MCPMessage, MCPPayload

# --- Pydantic Models for API Data Validation ---
# Defines the expected JSON structure for incoming queries from the frontend.
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    model_name: str = "gemini"

# Defines the JSON structure for responses sent back to the frontend.
class QueryResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[Dict[str, Any]]

# Initialize the main FastAPI application instance. This acts as our CoordinatorAgent.
app = FastAPI(
    title="Agentic RAG Coordinator",
    description="The central orchestration agent for the RAG chatbot."
)

# In-memory dictionary to store conversation histories for different sessions.
chat_histories: Dict[str, List[Dict[str, str]]] = {}

# --- Agent Initialization ---
# Create single, long-lived instances of our specialist agents.
retrieval_agent = RetrievalAgent()
ingestion_agent = IngestionAgent()
llm_response_agent = LLMResponseAgent()

# --- API Endpoints ---
@app.post("/upload")
async def handle_upload(files: List[UploadFile]):
    # 1. IngestionAgent processes and chunks the uploaded files.
    final_chunks = ingestion_agent.process_files(files)
    # 2. RetrievalAgent embeds and stores the chunks in the vector database.
    retrieval_agent.add_documents(final_chunks)
    return {"status": "success", "message": f"{len(files)} files processed and indexed."}

@app.post("/clear_session")
async def clear_session():
    global chat_histories
    # Clear both the conversation history and the document knowledge base.
    chat_histories = {}
    retrieval_agent.clear_collection()
    return {"status": "success", "message": "All chat histories and document knowledge have been cleared."}

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    # Ensure a session ID exists, creating one if it's a new conversation.
    session_id = request.session_id or str(uuid.uuid4())
    
    # Retrieve and update the chat history for the current session.
    history = chat_histories.get(session_id, [])
    history.append({"role": "user", "content": request.query})
    
    # --- Agent Orchestration Step 1: Retrieval ---
    retrieved_sources = retrieval_agent.search(request.query)
    
    # --- Agent Orchestration Step 2: MCP Construction ---
    # Package the retrieved context into a formal MCP message for inter-agent communication.
    mcp_payload = MCPPayload(
        retrieved_context=retrieved_sources,
        query=request.query
    )
    mcp_message = MCPMessage(
        sender="CoordinatorAgent",
        receiver="LLMResponseAgent",
        payload=mcp_payload
    )

    # --- Agent Orchestration Step 3: Generation ---
    try:
        # Pass the MCP data to the LLMResponseAgent to get the final answer.
        final_answer = llm_response_agent.generate_response(
            model_name=request.model_name,
            context_chunks=mcp_message.payload.retrieved_context,
            history=history,
            query=mcp_message.payload.query
        )
    # Gracefully handle API quota errors from external services.
    except ResourceExhausted as e:
        raise HTTPException(
            status_code=429, 
            detail="The daily API quota for the selected model has been exceeded. Please try again tomorrow or switch models."
        )
    # Handle any other unexpected errors during generation.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    # Update the chat history with the assistant's response.
    history.append({"role": "assistant", "content": final_answer})
    chat_histories[session_id] = history
    
    # Return the final, structured response to the frontend.
    return QueryResponse(
        answer=final_answer, 
        session_id=session_id,
        sources=retrieved_sources
    )