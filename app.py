from pathlib import Path
import sys
import streamlit as st
from service.vector_store import auto_build_vector_store
from utils import document_search
from web.chatbot import chat_message, add_scroll_style
from service.chatbot_service import ask_question 
import os
import base64
from web.assets.styles import GLOBAL_STYLES
# --- Page Setup ---
st.set_page_config(page_title="📘 PDF Chatbot", layout="wide")

add_scroll_style()

PDF_FOLDER = os.getenv("PDF_FOLDER", "data")

project_root = Path(__file__).resolve().parents[1]
src_dir = project_root / "src"

for path in [project_root, src_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


vendor_dir = project_root / PDF_FOLDER
vendor_dir.mkdir(parents=True, exist_ok=True)

doc_search_instance = document_search.DocumentSearchTool(pdf_folder_path=str(vendor_dir))
# Apply global CSS
st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)

# =====================================
# 💾 SESSION STATE
# =====================================
if "messages" not in st.session_state:
    st.session_state.messages = []  # [(role, content)]
if "active_page" not in st.session_state:
    st.session_state.active_page = "💬 Chat Assistant"

# --- Sidebar ---
with st.sidebar:
    st.image("TietoEvry_Logo_White.png", width=600)
    st.markdown(
        """<div style="text-align:center;padding:1rem;">
        <h2 style="font-size:22px;color:#1E3A8A;">Product Manual Assistant</h2></div>""",
        unsafe_allow_html=True
    )
    def go_chat():
        st.session_state.active_page = "💬 Chat Assistant"

    def go_admin():
        st.session_state.active_page = "⚙️ Admin Panel"

    st.button(
        "💬 Chat Assistant",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "💬 Chat Assistant" else "secondary",
        on_click=go_chat,
    )
    st.button(
        "⚙️ Admin Panel",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "⚙️ Admin Panel" else "secondary",
        on_click=go_admin,
    )

#     st.markdown("The assistant retrieves answers directly from your uploaded vendor manuals. "
#         "Answers are based on the content of vendor manuals (Fanuc, Siemens, Haas, etc.)")
#     st.markdown("<br>", unsafe_allow_html=True)  
#     uploaded_file = st.sidebar.file_uploader("Upload a manual in pdf format", type=["pdf"])
   
# # Save uploaded file and handle deletion
# if uploaded_file is not None:
#     output_dir = "data"
#     os.makedirs(output_dir, exist_ok=True)

#     # Try to delete existing files
#     deletion_failed = False
#     for filename in os.listdir(output_dir):
#         file_path = os.path.join(output_dir, filename)
#         if os.path.isfile(file_path):
#             try:
#                 os.remove(file_path)
#             except PermissionError:
#                 deletion_failed = True
#                 st.toast(f"Could not delete `{filename}`. It may be open in another program.")
#             except Exception as e:
#                 deletion_failed = True
#                 st.toast(f"Error deleting `{filename}`: {e}")

#     # Save new uploaded file
#     file_path = os.path.join(output_dir, uploaded_file.name)
#     try:
#         with open(file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         st.toast(f"Uploaded and saved: `{uploaded_file.name}`")
        
#         # Show spinner while building vector store
#         with st.spinner("Loading vector store. Please wait..."):
#             auto_build_vector_store()
#         # Clear chat history since data source changed
       
#         st.toast("New file uploaded and vector store updated.")
        
#     except Exception as e:
#         st.toast(f"Failed to save file: {e}")
    
    
# =====================================
# 💬 CHATBOT INTERFACE (UPDATED)
# =====================================

if st.session_state.active_page == "💬 Chat Assistant":
    st.title("💬 Product Manual Assistant")
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
            answer = ask_question(st.session_state.pending_query, history=st.session_state.history)

        # Store assistant message
        st.session_state.history.append({"role": "assistant", "message": answer})
        st.session_state.pending_query = None
        st.rerun()


# =====================================
# ⚙️ ADMIN PANEL (UPLOAD / DELETE / INDEX MANAGEMENT)
# =====================================
elif st.session_state.active_page == "⚙️ Admin Panel":

    st.title("⚙️ Admin - Manage Vendor Documents")

    # --- Vendor Docs ---
    st.subheader("📄 Manage Vendor Documents")
    st.caption(f"Files will be saved to: `{PDF_FOLDER}/`")
    # st.write(f"📁 Vendor Docs Path: `knowledge/{PDF_FOLDER}`")

    # Initialize the DocumentSearchTool (pass absolute folder path)
    document_search = doc_search_instance

    # =============================
    # ⚙️ Choose Vectorstore Action FIRST
    # =============================
    # st.subheader("📘 Vectorstore Update Mode")
    action = st.radio(
        "Choose how to handle vectorstore update:",
        ["Update Index (Incremental)", "Rebuild Index (Full)"],
        horizontal=True,
        key="vector_action"
    )

    # =============================
    # 🆕 Upload New Vendor PDFs
    # =============================
    vendor_files = st.file_uploader(
        "Upload new vendor PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_upload"
    )

    if vendor_files:
        new_files = []
        for f in vendor_files:
            save_path = vendor_dir / f.name
            with open(save_path, "wb") as out:
                out.write(f.getbuffer())
            new_files.append(f.name)

        if new_files:
            st.success(f"✅ Uploaded: {', '.join(new_files)}")

            with st.spinner("Processing PDFs..."):
                try:
                    if action == "Update Index (Incremental)":
                        document_search.update_vectorstore()
                        st.success("✅ Vectorstore incrementally updated.")
                    else:
                        document_search.build_vectorstore()
                        st.success("✅ Vectorstore rebuilt successfully.")
                except Exception as e:
                    st.error(f"❌ Vectorstore operation failed: {e}")

    # =============================
    # 🗑️ Delete Existing PDFs
    # =============================
    existing_files = [f.name for f in vendor_dir.iterdir() if f.is_file()]
    if existing_files:
        st.subheader("🗑️ Delete Existing PDFs")
        file_to_delete = st.multiselect("Select files to delete", existing_files)

        if st.button("Delete Selected Files"):
            if not file_to_delete:
                st.warning("⚠️ Please select at least one file to delete.")
            else:
                for fname in file_to_delete:
                    fpath = vendor_dir / fname
                    if fpath.exists():
                        fpath.unlink()
                st.success(f"🗑️ Deleted {len(file_to_delete)} file(s).")

                with st.spinner("Updating vectorstore after deletion..."):
                    try:
                        document_search.update_vectorstore()
                        st.info("✅ Vectorstore updated after deletion.")
                    except Exception as e:
                        st.error(f"❌ Vectorstore update failed: {e}")
    else:
        st.info("📭 No vendor documents available for deletion.")

    # # =============================
    # # ⚙️ Manual Vectorstore Controls
    # # =============================
    # st.divider()
    # st.subheader("⚙️ Vectorstore Management")

    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     if st.button("📦 Build Index (Full)"):
    #         with st.spinner("Building FAISS index from all PDFs..."):
    #             try:
    #                 document_search.build_vectorstore()
    #                 st.success("✅ Vectorstore rebuilt successfully.")
    #             except Exception as e:
    #                 st.error(f"❌ Build failed: {e}")

    # with col2:
    #     if st.button("📂 Load Index"):
    #         with st.spinner("Loading existing FAISS index..."):
    #             try:
    #                 vs = document_search.load_vectorstore()
    #                 if vs:
    #                     st.success("✅ FAISS index loaded successfully.")
    #                 else:
    #                     st.warning("⚠️ No existing index found.")
    #             except Exception as e:
    #                 st.error(f"❌ Load failed: {e}")

    # with col3:
    #     if st.button("🔁 Update Index"):
    #         with st.spinner("Updating FAISS index (check for changes)..."):
    #             try:
    #                 document_search.update_vectorstore()
    #                 st.success("✅ FAISS index updated successfully.")
    #             except Exception as e:
    #                 st.error(f"❌ Update failed: {e}")
