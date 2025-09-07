import uuid
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from google.api_core.exceptions import ResourceExhausted

from .agents.retrieval_agent import RetrievalAgent
from .agents.ingestion_agent import IngestionAgent
from .agents.llm_response_agent import LLMResponseAgent
from .mcp_models import MCPMessage, MCPPayload

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    model_name: str = "gemini"

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[Dict[str, Any]]

app = FastAPI(
    title="Agentic RAG Coordinator",
    description="The central orchestration agent for the RAG chatbot."
)

chat_histories: Dict[str, List[Dict[str, str]]] = {}

retrieval_agent = RetrievalAgent()
ingestion_agent = IngestionAgent()
llm_response_agent = LLMResponseAgent()

@app.post("/upload")
async def handle_upload(files: List[UploadFile]):
    final_chunks = ingestion_agent.process_files(files)
    retrieval_agent.add_documents(final_chunks)
    return {"status": "success", "message": f"{len(files)} files processed and indexed."}

@app.post("/clear_session")
async def clear_session():
    global chat_histories
    chat_histories = {}
    retrieval_agent.clear_collection()
    return {"status": "success", "message": "All chat histories and document knowledge have been cleared."}

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    history = chat_histories.get(session_id, [])
    history.append({"role": "user", "content": request.query})
    
    retrieved_sources = retrieval_agent.search(request.query)
    
    mcp_payload = MCPPayload(
        retrieved_context=retrieved_sources,
        query=request.query
    )
    mcp_message = MCPMessage(
        sender="CoordinatorAgent",
        receiver="LLMResponseAgent",
        payload=mcp_payload
    )

    try:
        final_answer = llm_response_agent.generate_response(
            model_name=request.model_name,
            context_chunks=mcp_message.payload.retrieved_context,
            history=history,
            query=mcp_message.payload.query
        )
    except ResourceExhausted as e:
        raise HTTPException(
            status_code=429, 
            detail="The daily API quota for the selected model has been exceeded. Please try again tomorrow or switch models."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    history.append({"role": "assistant", "content": final_answer})
    chat_histories[session_id] = history
    
    return QueryResponse(
        answer=final_answer, 
        session_id=session_id,
        sources=retrieved_sources
    )