import os
import time
import hashlib
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
from PyPDF2 import PdfReader

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

# ---- Azure Config ----
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION", "2023-05-15")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")

VECTORSTORE_PATH = "backend/vectorstore/vendor_docs_embeddings"
HASH_PATH = "backend/vectorstore/pdf_index_meta.json"  # store hash of current PDF

# ------------------------------
# Get Azure OpenAI Embeddings
# ------------------------------
def get_azure_embeddings():
    if not all([AZURE_API_KEY, AZURE_ENDPOINT, AZURE_EMBEDDING_DEPLOYMENT]):
        raise ValueError(
            "Missing Azure OpenAI credentials. Please set "
            "AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_EMBEDDING_DEPLOYMENT_NAME in your .env file."
        )

    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
        model=AZURE_EMBEDDING_DEPLOYMENT,
    )

# ------------------------------
# Extract text from PDF
# ------------------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ------------------------------
# Split text into chunks
# ------------------------------
def split_text_into_chunks(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_text(text)

# ------------------------------
# Build FAISS vector store with batching
# ------------------------------
def build_vector_store(pdf_path: str, batch_size: int = 50, delay: float = 1.0):
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)
    print(f"Creating {len(chunks)} document chunks...")

    documents = [Document(page_content=chunk) for chunk in chunks]
    embeddings = get_azure_embeddings()

    # Batch embeddings to avoid rate limits
    faiss_index = None
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} / {((len(documents)-1)//batch_size)+1}...")
        batch_index = FAISS.from_documents(batch_docs, embeddings)

        if faiss_index is None:
            faiss_index = batch_index
        else:
            faiss_index.merge_from(batch_index)

        time.sleep(delay)  # small delay to avoid hitting rate limits

    os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)
    faiss_index.save_local(VECTORSTORE_PATH)
    print(f"✅ Vector store saved at: {VECTORSTORE_PATH}")

    # Save hash of PDF
    pdf_hash = hashlib.md5(open(pdf_path, "rb").read()).hexdigest()
    with open(HASH_PATH, "w") as f:
        f.write(pdf_hash)

# ------------------------------
# Load FAISS vector store
# ------------------------------
def load_vector_store():
    if not os.path.exists(VECTORSTORE_PATH):
        raise FileNotFoundError("Vector store not found. Run build_vector_store() first.")
    embeddings = get_azure_embeddings()
    return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)

# ------------------------------
# Auto-build vector store for PDFs in folder
# ------------------------------
def auto_build_vector_store(folder="data"):
    pdf_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in folder. Skipping vector store build.")
        return

    # For simplicity, use the first PDF (you can extend to merge multiple PDFs)
    pdf_path = pdf_files[0]
    pdf_hash = hashlib.md5(open(pdf_path, "rb").read()).hexdigest()

    # Check existing hash
    existing_hash = None
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, "r") as f:
            existing_hash = f.read().strip()

    # Rebuild only if PDF changed or vectorstore missing
    if existing_hash != pdf_hash or not os.path.exists(VECTORSTORE_PATH):
        if os.path.exists(VECTORSTORE_PATH):
            print("PDF changed. Removing old vector store...")
            import shutil
            shutil.rmtree(VECTORSTORE_PATH)
        build_vector_store(pdf_path)
    else:
        print("Vector store already exists and PDF unchanged. Skipping rebuild.")

# ------------------------------
# Run auto-build if executed directly
# ------------------------------
if __name__ == "__main__":
    auto_build_vector_store()
