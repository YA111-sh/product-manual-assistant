import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import AzureOpenAIEmbeddings


# ---------------------------------------------------------------------
#  Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")
AZURE_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
AZURE_EMBEDDING_MODEL_NAME = os.getenv("AZURE_EMBEDDING_MODEL_NAME")
# ---------------------------------------------------------------------
# 1. Input Schema
# ---------------------------------------------------------------------
class DocumentSearchInput(BaseModel):
    customer_question: str = Field(
        ...,
        description="Customer's question or issue to resolve from vendor documents."
    )


# ---------------------------------------------------------------------
# 2. DocumentSearchTool Definition
# ---------------------------------------------------------------------
class DocumentSearchTool(BaseTool):
    name: str = "DocumentSearchTool"
    description: str = "Searches semantically relevant content from vendor PDF documents."

    pdf_folder_path: str = "data"
    index_dir: Optional[str] = None
    k: int = 5

    embeddings: Optional[AzureOpenAIEmbeddings] = None
    vectorstore: Optional[FAISS] = None
    meta_file: Optional[Path] = None

    # -----------------------------------------------------------------
    # setup()
    # -----------------------------------------------------------------
    def setup(self):
        """Initialize embeddings and prepare paths."""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
        model = os.getenv("AZURE_EMBEDDING_MODEL_NAME")

        if not all([api_key, endpoint, deployment]):
            raise EnvironmentError(
                "Missing Azure OpenAI credentials. "
                "Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_EMBEDDING_DEPLOYMENT."
            )

        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=deployment,
            model=model,
            api_key=api_key,
            azure_endpoint=endpoint,
        )

        self.index_dir = Path(self.index_dir or "backend/vectorstore/vendor_docs_embeddings")
        self.meta_file = self.index_dir / "pdf_index_meta.json"
        self.index_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # Helper: File Hash
    # -----------------------------------------------------------------
    def _compute_file_hash(self, filepath: str) -> str:
        stat = os.stat(filepath)
        hash_md5 = hashlib.md5()
        hash_md5.update(filepath.encode("utf-8"))
        hash_md5.update(str(stat.st_mtime).encode("utf-8"))
        return hash_md5.hexdigest()

    # -----------------------------------------------------------------
    # Helper: Metadata Load
    # -----------------------------------------------------------------
    def _load_meta_file(self) -> dict:
        if self.meta_file.exists():
            try:
                with open(self.meta_file, "r") as f:
                    text = f.read().strip()
                    return json.loads(text) if text else {"files": {}}
            except json.JSONDecodeError:
                return {"files": {}}
        return {"files": {}}

    # -----------------------------------------------------------------
    # Independent: Build vectorstore from scratch
    # -----------------------------------------------------------------
    def build_vectorstore(self) -> FAISS:
        """Rebuild the FAISS vectorstore from all PDFs."""
        self.setup()

        pdf_path = Path(self.pdf_folder_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ PDF folder not found: {pdf_path}")

        pdf_files = [str(pdf_path / f) for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]
        vectorstore = self._prepare_vectorstore(pdf_files)

        # Save index and metadata
        current_files = {
            f: self._compute_file_hash(str(pdf_path / f))
            for f in os.listdir(pdf_path)
            if f.lower().endswith(".pdf")
        }
        vectorstore.save_local(str(self.index_dir))
        with open(self.meta_file, "w") as f:
            json.dump({"files": current_files}, f)

        print(f"✅ FAISS index built successfully at {self.index_dir}")
        self.vectorstore = vectorstore
        return vectorstore

    # -----------------------------------------------------------------
    # Independent: Load existing vectorstore
    # -----------------------------------------------------------------
    def load_vectorstore(self) -> Optional[FAISS]:
        """Load FAISS vectorstore if exists."""
        self.setup()

        index_file = self.index_dir / "index.faiss"
        store_file = self.index_dir / "index.pkl"

        if not (index_file.exists() and store_file.exists()):
            print("⚠️ No existing FAISS index found. Please build it first.")
            return None

        print(f"✅ Loading FAISS index from {self.index_dir}")
        self.vectorstore = FAISS.load_local(
            str(self.index_dir),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )
        return self.vectorstore

    # -----------------------------------------------------------------
    # Independent: Update vectorstore (add/update/delete PDFs)
    # -----------------------------------------------------------------
    def update_vectorstore(self) -> FAISS:
        """Compare PDFs and update FAISS index."""
        self.setup()

        pdf_path = Path(self.pdf_folder_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ PDF folder not found: {pdf_path}")

        current_files = {
            f: self._compute_file_hash(str(pdf_path / f))
            for f in os.listdir(pdf_path)
            if f.lower().endswith(".pdf")
        }

        saved_meta = self._load_meta_file()
        saved_files = saved_meta.get("files", {})

        vectorstore = self.load_vectorstore()
        if vectorstore is None:
            print("⚠️ No existing index found. Building a new one.")
            return self.build_vectorstore()

        # Detect differences
        to_add = [f for f in current_files if f not in saved_files]
        to_update = [f for f in current_files if f in saved_files and saved_files[f] != current_files[f]]
        to_delete = [f for f in saved_files if f not in current_files]

        if not any([to_add, to_update, to_delete]):
            print("✅ No changes detected. Index is up-to-date.")
            return vectorstore

        if to_delete or to_update:
            print("🔄 Rebuilding FAISS index due to updated/deleted files...")
            return self.build_vectorstore()

        if to_add:
            print(f"➕ Adding new PDFs: {to_add}")
            new_paths = [str(pdf_path / f) for f in to_add]
            new_store = self._prepare_vectorstore(new_paths)
            vectorstore.merge_from(new_store)

            # Save updated index + metadata
            vectorstore.save_local(str(self.index_dir))
            with open(self.meta_file, "w") as f:
                json.dump({"files": current_files}, f)

            print(f"✅ FAISS index updated with new PDFs.")
            self.vectorstore = vectorstore
            return vectorstore

    # -----------------------------------------------------------------
    # Internal: Prepare FAISS store from files
    # -----------------------------------------------------------------
    def _prepare_vectorstore(self, files: List[str]) -> FAISS:
        all_chunks = []
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"⚠️ File not found: {file_path}, skipping.")
                continue

            loader = PyPDFLoader(file_path)
            docs = loader.load()
            file_size = os.path.getsize(file_path)
            chunk_size = 500 if file_size < 1_000_000 else 1000

            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
            chunks = splitter.split_documents(docs)

            for i, chunk in enumerate(chunks):
                chunk.metadata["source_doc"] = os.path.basename(file_path)
                chunk.metadata["chunk_id"] = f"{os.path.basename(file_path)}::chunk::{i}"
                chunk.metadata["page"] = chunk.metadata.get("page", None)

            all_chunks.extend(chunks)

        if not all_chunks:
            raise ValueError("❌ No PDF content found to index.")

        print(f"📚 Creating FAISS vectorstore from {len(all_chunks)} chunks...")
        return FAISS.from_documents(all_chunks, embedding=self.embeddings)

    # -----------------------------------------------------------------
    # Search API
    # -----------------------------------------------------------------
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search documents."""
        if self.vectorstore is None:
            self.load_vectorstore()

        top_k = top_k or self.k
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)

        results = []
        for doc, score in docs_and_scores:
            text = doc.page_content.strip()
            results.append({
                "filename": doc.metadata.get("source_doc", "Unknown"),
                "page": doc.metadata.get("page"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "excerpt": text[:300] + ("..." if len(text) > 300 else ""),
                "text": text,
                "score": float(score) if score else None,
            })
        return results

    # -----------------------------------------------------------------
    # CrewAI Run Hook
    # -----------------------------------------------------------------
    def _run(self, customer_question: str) -> str:
        results = self.search(customer_question, top_k=self.k)
        if not results:
            return "Sorry! No relevant documents found."
        formatted = [f"**{r['filename']} | Page: {r.get('page', '?')}**\n{r['text']}" for r in results]
        return "\n\n---\n\n".join(formatted)
