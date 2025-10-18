import streamlit as st
from service.vector_store import auto_build_vector_store
from web.chatbot import chat_message, add_scroll_style
from service.chatbot_service import ask_question 
import os
import base64

# --- Page Setup ---
st.set_page_config(page_title="📘 PDF Chatbot", layout="wide")

add_scroll_style()


# --- Sidebar ---
with st.sidebar:
    #st.header("Manuals & Documents")
    #st.image("web/assets/2.jpg")
    st.header(
        "Manuals & Documents"
    )
    st.markdown("The assistant retrieves answers directly from your uploaded vendor manuals. "
        "Answers are based on the content of vendor manuals (Fanuc, Siemens, Haas, etc.)")
    st.markdown("<br>", unsafe_allow_html=True)  
    uploaded_file = st.sidebar.file_uploader("Upload a manual in pdf format", type=["pdf"])
   
# Save uploaded file and handle deletion
if uploaded_file is not None:
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # Try to delete existing files
    deletion_failed = False
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                deletion_failed = True
                st.toast(f"Could not delete `{filename}`. It may be open in another program.")
            except Exception as e:
                deletion_failed = True
                st.toast(f"Error deleting `{filename}`: {e}")

    # Save new uploaded file
    file_path = os.path.join(output_dir, uploaded_file.name)
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.toast(f"Uploaded and saved: `{uploaded_file.name}`")
        
        # Show spinner while building vector store
        with st.spinner("Loading vector store. Please wait..."):
            auto_build_vector_store()
        # Clear chat history since data source changed
       
        st.toast("New file uploaded and vector store updated.")
        
    except Exception as e:
        st.toast(f"Failed to save file: {e}")
    
    
    
# --- Initialize session_state ---
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# --- Chat Input ---
query = st.chat_input("Ask something about the product manual...")

# --- Display chat messages ---
for chat in st.session_state.history:
    chat_message(chat["role"], chat["message"])

# --- Handle new user query ---
if query:
    # Add user message immediately
    st.session_state.history.append({"role": "user", "message": query})
    st.session_state.pending_query = query
    st.rerun()  # ✅ re-run to show instantly

# --- Process assistant response ---
if st.session_state.pending_query:
    with st.spinner("🤖 Assistant is thinking..."):
        # 🧠 Call the agent-based manager
        answer = ask_question(st.session_state.pending_query)

    # Store assistant message
    st.session_state.history.append({"role": "assistant", "message": answer})
    st.session_state.pending_query = None
    st.rerun()
