import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3"

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/app/data/chroma_db")
REGULATIONS_DIR = os.getenv("REGULATIONS_DIR", "/app/data/regulations")
CONTRACTS_DIR = os.getenv("CONTRACTS_DIR", "/app/data/contracts")
AUDIT_DB_PATH = os.getenv("AUDIT_DB_PATH", "/app/logs/audit.db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
