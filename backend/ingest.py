"""Document ingestion: load PDFs and HTML contracts, chunk them, store in ChromaDB."""

import os
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import (
    CHROMA_PERSIST_DIR,
    REGULATIONS_DIR,
    CONTRACTS_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def extract_pdf_text(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def extract_html_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n", strip=True)


def load_documents(directory: str, doc_type: str) -> list[dict]:
    docs = []
    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
        if fname.endswith(".pdf"):
            text = extract_pdf_text(path)
        elif fname.endswith((".html", ".htm")):
            text = extract_html_text(path)
        else:
            continue
        docs.append({
            "text": text,
            "metadata": {
                "source": fname,
                "type": doc_type,
                "path": path,
            },
        })
        print(f"  Loaded: {fname} ({len(text)} chars)")
    return docs


def build_vectorstore():
    print("Loading regulations...")
    reg_docs = load_documents(REGULATIONS_DIR, "regulation")
    print("Loading contracts...")
    contract_docs = load_documents(CONTRACTS_DIR, "contract")

    all_docs = reg_docs + contract_docs

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
    )

    texts = []
    metadatas = []
    for doc in all_docs:
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append(doc["metadata"])

    print(f"Total chunks: {len(texts)}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"Vectorstore built at {CHROMA_PERSIST_DIR}")
    return vectorstore


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


if __name__ == "__main__":
    build_vectorstore()
