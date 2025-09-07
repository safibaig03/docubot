import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(page_title="DocuBot", page_icon="📄", layout="wide")

# --- Constants ---
# URL of the FastAPI backend server
BACKEND_URL = "http://127.0.0.1:8000"

# --- Custom Styling ---
# Inject custom CSS for a cleaner look
st.markdown("""
<style>
    .stChatMessage { text-align: left; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
# Streamlit's way to maintain state across user interactions (reruns)
# Initialize a unique session ID for the conversation
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
# Initialize the list to store chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []
# Initialize a flag to track if documents have been processed
if 'processed' not in st.session_state:
    st.session_state.processed = False

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("📄 DocuBot Controls")
    
    st.subheader("1. Select LLM")
    model_choice = st.selectbox(
        "Choose your Large Language Model:",
        ("gemini", "groq", "huggingface"),
        label_visibility="collapsed"
    )

    st.subheader("2. Upload Your Documents")
    uploaded_files = st.file_uploader(
        "Upload your documents here.",
        type=["pdf", "docx", "pptx", "csv", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # Button to trigger the document ingestion process
    if st.button("Process Documents", type="primary"):
        if uploaded_files:
            # Use a status container for better user feedback during processing
            with st.status("Processing documents...", expanded=True) as status:
                # Prepare files in the format required by FastAPI for multipart/form-data
                files_to_send = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                try:
                    # Make the API call to the backend's /upload endpoint
                    response = requests.post(f"{BACKEND_URL}/upload", files=files_to_send, timeout=600)
                    if response.status_code == 200:
                        status.update(label="✅ Documents Processed!", state="complete", expanded=False)
                        st.session_state.processed = True
                    else:
                        status.update(label="⚠️ Error processing!", state="error", expanded=True)
                        st.error(f"Error: {response.text}")
                except requests.exceptions.RequestException as e:
                    status.update(label="⚠️ Connection Error!", state="error", expanded=True)
                    st.error(f"Failed to connect to backend: {e}")
        else:
            st.warning("Please upload at least one document.")
    
    st.subheader("3. Session Controls")
    # Button to clear both the backend (DB and history) and frontend state
    if st.button("Clear Session (Chat & Docs)"):
        try:
            # Call the backend endpoint to clear its state
            requests.post(f"{BACKEND_URL}/clear_session")
            # Clear the local frontend state
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.processed = False
            # Force a rerun of the script to refresh the UI
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to clear session: {e}")

# --- Main Chat Interface ---
st.header("Ask Your Documents Anything", divider='rainbow')

# Display a welcome message if no documents have been processed yet
if not st.session_state.processed:
    st.info("Welcome to DocuBot! Please select a model, then upload and process your documents to begin.")

# Display existing chat messages from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message is from the assistant, show the sources it used
        if "sources" in message:
            with st.expander("📚 View Sources"):
                for source in message["sources"]:
                    metadata = source.get('metadata', {})
                    source_info = f"**{metadata.get('source', 'N/A')}**"
                    if 'page' in metadata:
                        source_info += f" (Page: {metadata['page']})"
                    st.markdown(f"**{source_info}**")
                    st.markdown(f"> {source.get('content', 'No content available.')}")
                    st.markdown("---")

# Input for new user questions
if prompt := st.chat_input("What is this document about?"):
    # Ensure documents are processed before allowing questions
    if not st.session_state.processed:
        st.warning("Please process your documents before asking questions.")
    else:
        # Add user's new message to the local chat history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process and display the assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Construct the payload to send to the backend
                payload = {
                    "query": prompt, 
                    "session_id": st.session_state.session_id,
                    "model_name": model_choice
                }
                try:
                    # Make the API call to the backend's /query endpoint
                    response = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=300)
                    if response.status_code == 200:
                        response_data = response.json()
                        response_text = response_data["answer"]
                        sources = response_data["sources"]
                        
                        # Display the main answer
                        st.markdown(response_text)
                        
                        # Update the session ID with the one from the backend (important for the first message)
                        st.session_state.session_id = response_data["session_id"]
                        # Add the full response (including sources) to our local history
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": sources})
                        # Rerun the script to display the sources correctly
                        st.rerun()

                    else:
                        st.error(f"Error from backend: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection to backend failed: {e}")