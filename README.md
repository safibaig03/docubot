Agentic RAG Chatbot for Multi-Format Document QA

This project is a sophisticated, agent-based Retrieval-Augmented Generation (RAG) chatbot built to answer questions from a knowledge base of user-uploaded documents. It leverages a modern, modular architecture using specialized AI agents, a formal communication protocol (MCP), and support for multiple leading Large Language Models.

Features
📄 Multi-Format Document Support: Natively parses and understands .pdf, .docx, .pptx, .csv, and .txt files.

🤖 Agentic Architecture: Employs a robust, decoupled system where a central CoordinatorAgent orchestrates tasks between specialized agents for Ingestion, Retrieval, and LLMResponse generation.

🔄 Multi-LLM Backend: Allows users to seamlessly switch between different Large Language Models at runtime, including Google Gemini, Groq (Llama 3.1), and Hugging Face (Llama 3).

📚 Source-Cited Responses: Every answer is backed by the specific text chunks from the source documents, which can be viewed for verification.

🧠 Conversational Memory: Maintains session-based chat history, enabling contextual, multi-turn conversations.

✨ Modern & Clean UI: A visually appealing, centered-layout chatbot interface built with Streamlit.

🔄 Full Session Control: Users can clear the entire session, including the chat history and the document knowledge base, to start fresh.

🛡️ Robust Error Handling: Gracefully manages external API errors, such as rate limits, providing clear feedback to the user.

Architecture
The application is built on a decoupled, two-part system: a FastAPI backend that serves as the "brain," and a Streamlit frontend that serves as the user interface.


System Flow
Ingestion: The user uploads documents via the UI. The CoordinatorAgent (FastAPI) receives these files and delegates the task to the IngestionAgent, which parses the documents into text chunks with metadata. These chunks are then passed to the RetrievalAgent.

Indexing: The RetrievalAgent creates vector embeddings for each chunk using a SentenceTransformer model and stores them in an in-memory ChromaDB collection.

Querying: When the user asks a question, the CoordinatorAgent asks the RetrievalAgent to find the most relevant document chunks.

MCP Communication: The retrieved context is packaged into a formal Model Context Protocol (MCP) message and passed internally to the LLMResponseAgent.

Generation: The LLMResponseAgent uses the selected LLM (Gemini, Groq, etc.), the retrieved context, and the chat history to synthesize a final, coherent answer.

Project Structure
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

Tech Stack
Backend Framework: FastAPI

Frontend UI: Streamlit

Web Server: Uvicorn

Vector Database: ChromaDB (in-memory)

Embedding Model: sentence-transformers/all-MiniLM-L6-v2

LLM Providers: Google Gemini, Groq, Hugging Face

Core Libraries: Pydantic, LangChain (Text Splitters), python-docx, pypdf

Package Manager: uv

Setup and Installation
Follow these steps to set up the project locally on a Windows machine.

1. Clone the Repository
git clone https://github.com/safibaig03/docubot
cd agentic-rag-chatbot

2. Create and Activate Virtual Environment
This project uses uv for fast and efficient package management.

# Create the virtual environment
uv venv

# Activate the environment
.\.venv\Scripts\activate

3. Install Dependencies
All required libraries are listed in requirements.txt.

uv pip install -r requirements.txt

4. Set Up Environment Variables

GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
HUGGINGFACE_API_KEY="YOUR_HUGGINGFACE_API_KEY_HERE"

5. Run the Application
Terminal 1: Run the Backend Server
Make sure your virtual environment is active.

uvicorn app.main:app --reload

The backend will be available at http://127.0.0.1:8000.

Terminal 2: Run the Frontend UI
Make sure your virtual environment is active in this terminal as well.

streamlit run ui/app.py

OR 

In a PowerShell terminal, simply run:

.\start.bat

This will open two new terminal windows for the backend and frontend automatically.
