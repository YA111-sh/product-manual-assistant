import streamlit as st
from web.chatbot import chat_message, add_scroll_style
from service.chatbot_service import handle_query,handle_query_with_crew 



# --- Page Setup ---
st.set_page_config(page_title="📘 PDF Chatbot", layout="wide")
add_scroll_style()

# st.title("Product Manual Assistant")
st.markdown("""
    <h2 style="text-align:center; color:#1E3A8A;">
        🤖 Product Manual Assistant
    </h2>
    <p style="text-align:center;">Ask any question about your machine or equipment manuals.</p>
""", unsafe_allow_html=True)
# st.markdown("Ask questions about your product manual below")

# Sidebar
with st.sidebar:
    st.header("📂 Manuals & Documents")
    st.info("The assistant retrieves answers directly from your uploaded vendor manuals. Answers are based on the content of vendor manuals (Fanuc, Siemens, Haas, etc.)")
    
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
        answer = handle_query_with_crew(st.session_state.pending_query)

    # Store assistant message
    st.session_state.history.append({"role": "assistant", "message": answer})
    st.session_state.pending_query = None
    st.rerun()
