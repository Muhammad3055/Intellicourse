# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from app.config import VECTOR_DB_PATH
# import os

# def prepare_vector_store():
#     """Load PDFs, split into chunks, embed them, and store in ChromaDB."""
#     docs = []
#     data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

#     for file in [
#         "BUS_Catalog_Fall_2025.pdf",
#         "MATH_Catalog_Fall_2025.pdf",
#         "BIO_Catalog_Fall_2025.pdf",
#         "LAW_Catalog_Fall_2025.pdf",
#         "CS_Catalog_Fall_2025.pdf"
#     ]:
#         file_path = os.path.join(data_dir, file)
#         if not os.path.exists(file_path):
#             print(f"⚠️ Skipping missing file: {file_path}")
#             continue
#         loader = PyPDFLoader(file_path)
#         docs.extend(loader.load())

#     splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
#     chunks = splitter.split_documents(docs)

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     vectordb = Chroma.from_documents(
#         documents=chunks,
#         embedding=embeddings,
#         persist_directory=VECTOR_DB_PATH
#     )
#     return vectordb


# def get_retriever():
#     """Load the existing vector store and return a retriever."""
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     vectordb = Chroma(
#         persist_directory=VECTOR_DB_PATH,
#         embedding_function=embeddings
#     )
#     return vectordb.as_retriever()


# if __name__ == "__main__":
#     vectordb = prepare_vector_store()
#     retriever = get_retriever()
#     print("✅ Vector DB ready at:", VECTOR_DB_PATH)

#     while True:
#         query = input("\n💬 Enter your query (or type 'exit' to quit): ")
#         if query.lower() == "exit":
#             break

#         docs = retriever.get_relevant_documents(query)
#         if not docs:
#             print("⚠️ No results found. Try keywords like 'CS 482' or 'Applied Machine Learning'.")
#         else:
#             seen = set()
#             for i, d in enumerate(docs, 1):
#                 snippet = d.page_content.strip()
#                 if snippet not in seen:
#                     print(f"{i}. {snippet[:400]}...\n")
#                     seen.add(snippet)
# filepath: app/rag.py
# =========================================
# filepath: app/rag.py
# filepath: app/rag.py
from __future__ import annotations
import os
import re
from typing import Dict, Optional, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import VECTOR_DB_PATH

PDF_FILES = [
    "BUS_Catalog_Fall_2025.pdf",
    "MATH_Catalog_Fall_2025.pdf",
    "BIO_Catalog_Fall_2025.pdf",
    "LAW_Catalog_Fall_2025.pdf",
    "CS_Catalog_Fall_2025.pdf",
]

# -----------------------------
# Helpers
# -----------------------------
def _data_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def _load_docs():
    docs = []
    data_dir = _data_dir()
    for fname in PDF_FILES:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            print(f"⚠️ Skipping missing file: {path}")
            continue
        loader = PyPDFLoader(path)
        docs.extend(loader.load())
    return docs

# -----------------------------
# Vector DB setup
# -----------------------------
def prepare_vector_store(rebuild: bool = False) -> Tuple[Chroma, bool]:
    """Build/refresh Chroma from PDFs. Returns (db, created_flag)."""
    if rebuild and os.path.isdir(VECTOR_DB_PATH):
        for root, dirs, files in os.walk(VECTOR_DB_PATH, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except OSError:
                    pass

    docs = _load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=VECTOR_DB_PATH)
    return db, True

def get_retriever(k: int = 6, use_mmr: bool = True, score_threshold: Optional[float] = None):
    """
    Retriever for ALL courses (CS, BIO, MATH, BUS, LAW).
    Falls back to similarity search if threshold filters everything.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

    if score_threshold is not None:
        retriever = db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": k, "score_threshold": score_threshold},
        )
    elif use_mmr:
        retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": 24, "lambda_mult": 0.5},
        )
    else:
        retriever = db.as_retriever(search_kwargs={"k": k})

    # ✅ Safe wrapper
    def safe_get(query: str):
        try:
            docs = retriever.invoke(query)  # LC 0.2 style
        except Exception:
            docs = retriever.get_relevant_documents(query)  # fallback
        if not docs:
            return db.similarity_search(query, k=k)
        return docs

    class SafeRetriever:
        def __init__(self, retriever, safe_get):
            self._retriever = retriever
            self._safe_get = safe_get
        def get_relevant_documents(self, query: str):
            return self._safe_get(query)

    return SafeRetriever(retriever, safe_get)

# -----------------------------
# Deterministic extractor
# -----------------------------
_CODE_RX = re.compile(r"\b(Course\s*Code|Code)\s*:\s*([A-Z]{2,4}\s*\d{3})", re.I)
_TITLE_RX = re.compile(r"\b(Course\s*Title|Title)\s*:\s*(.+)", re.I)
_PREQ_RX = re.compile(r"\bPrerequisites?\s*:\s*(.+)", re.I)

def extract_course_info(text: str) -> Dict[str, str]:
    """Extract Course Code, Title, and Prerequisites from raw catalog text."""
    code, title, prereq = None, None, None
    for line in text.splitlines():
        if not code:
            m = _CODE_RX.search(line)
            if m: code = m.group(2).upper().replace("  ", " ").strip()
        if not title:
            m = _TITLE_RX.search(line)
            if m: title = m.group(2).strip()
        if not prereq:
            m = _PREQ_RX.search(line)
            if m: prereq = m.group(1).strip().rstrip(".")
        if code and title and prereq:
            break
    return {"code": code or "", "title": title or "", "prereq": prereq or ""}

# -----------------------------
# CLI Test
# -----------------------------
if __name__ == "__main__":
    db, _ = prepare_vector_store(rebuild=False)
    retriever = get_retriever()
    print("✅ Vector DB ready at:", VECTOR_DB_PATH)

    while True:
        q = input("\n💬 Enter query (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        docs = retriever.get_relevant_documents(q)
        if not docs:
            print("⚠️ No results. Try keywords like 'CS 482' or 'Applied Machine Learning'.")
            continue
        concat = "\n".join(d.page_content for d in docs[:4])
        info = extract_course_info(concat)
        if info["code"] or info["prereq"] or info["title"]:
            print(f"\n• Course Code: {info['code'] or 'unknown'}")
            print(f"• Title: {info['title'] or 'unknown'}")
            print(f"• Prerequisites: {info['prereq'] or 'not stated'}\n")
        else:
            for i, d in enumerate(docs[:4], 1):
                src = d.metadata.get("source") or d.metadata.get("file_path") or "catalog"
                page = d.metadata.get("page", "?")
                snippet = " ".join(d.page_content.strip().split())
                print(f"{i}. [{src}#p{page}] {snippet[:400]}...")
