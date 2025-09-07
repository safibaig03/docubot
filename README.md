🧠 Agentic RAG Chatbot with MCP (LangGraph + LangChain)

Agentic RAG Chatbot with MCPThis project is a Retrieval-Augmented Generation (RAG) chatbot that answers user queries using uploaded documents. It is built with a custom agentic architecture using FastAPI and Streamlit, and follows a Model Context Protocol (MCP) for inter-agent communication.
---


🚀 Features

✅ Multi-Format Document Support: Natively parses and understands .pdf, .docx, .pptx, .csv, and .txt files.
🧠 Custom Agentic Architecture:CoordinatorAgent (FastAPI): Orchestrates the entire workflow.
IngestionAgent: Parses and splits documents.
RetrievalAgent: Embeds chunks and performs semantic search.
LLMResponseAgent: Synthesizes answers from context.
🔗 Model Context Protocol (MCP) for structured, in-memory message passing.
🔄 Multi-LLM Support: Switch between Google Gemini, Groq (Llama 3.1), and Hugging Face models.
🌐 Streamlit UI for file uploads, multi-turn Q&A, and viewing source citations.




🧱 Tech Stack
Layer                Tool
LLM Providers        Google Gemini, Groq, Hugging Face
Embeddings           sentence-transformers/all-MiniLM-L6-v2
Vector DB            ChromaDB 
Backend              FastAPI
Frontend             Streamlit
Protocol             Custom MCP (Pydantic)
Package Manager      uv




📁 Project Structure 
agentic-rag-chatbot/
  ├── app/
  │   ├── agents/
  │   │   ├── __init__.py
  │   │   ├── ingestion_agent.py
  │   │   ├── llm_response_agent.py
  │   │   └── retrieval_agent.py
  │   ├── __init__.py
  │   ├── main.py
  │   └── mcp_models.py
  ├── ui/
  │   └── app.py
  ├── .env
  ├── .gitignore
  ├── README.md
  ├── requirements.txt
  └── start.bat


  
🛠️ Setup Instructions

1. 📦 Install DependenciesMake sure you are in the project's root directory.# Create and activate virtual environment
uv venv
.\.venv\Scripts\activate

# Install requirements
uv pip install -r requirements.txt

2. 🔑 Set API KeysCreate a .env file in the project's root directory. Add your API keys:GOOGLE_API_KEY="Get your key from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)"
GROQ_API_KEY="Get your key from [https://console.groq.com/keys](https://console.groq.com/keys)"
HUGGINGFACE_API_KEY="Get your key from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)"

3. 🖥️ Launch the ApplicationYou need to run the backend and frontend in two separate terminals. A start.bat script is included for convenience on 

Windows.(using the script):.\start.bat

Manual Method:

In Terminal 1 (Backend):uvicorn app.main:app --reload
In Terminal 2 (Frontend):streamlit run ui/app.py

