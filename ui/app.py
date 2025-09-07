import streamlit as st
import requests
import time

st.set_page_config(page_title="DocuBot", page_icon="📄", layout="wide")

BACKEND_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
    .stChatMessage { text-align: left; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'processed' not in st.session_state:
    st.session_state.processed = False

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

    if st.button("Process Documents", type="primary"):
        if uploaded_files:
            with st.status("Processing documents...", expanded=True) as status:
                files_to_send = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                try:
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
    if st.button("Clear Session (Chat & Docs)"):
        try:
            requests.post(f"{BACKEND_URL}/clear_session")
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.processed = False
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to clear session: {e}")

st.header("Ask Your Documents Anything", divider='rainbow')

if not st.session_state.processed:
    st.info("Welcome to DocuBot! Please select a model, then upload and process your documents to begin.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
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

if prompt := st.chat_input("What is this document about?"):
    if not st.session_state.processed:
        st.warning("Please process your documents before asking questions.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {
                    "query": prompt, 
                    "session_id": st.session_state.session_id,
                    "model_name": model_choice
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=300)
                    if response.status_code == 200:
                        response_data = response.json()
                        response_text = response_data["answer"]
                        sources = response_data["sources"]
                        
                        st.markdown(response_text)
                        
                        st.session_state.session_id = response_data["session_id"]
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": sources})
                        st.rerun()

                    else:
                        st.error(f"Error from backend: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection to backend failed: {e}")