"""FastAPI backend for the compliance analysis system."""

import os
import re
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from fastapi.responses import FileResponse

from config import GROQ_API_KEY, GROQ_WHISPER_MODEL, CONTRACTS_DIR
from agents import analyze_contract
from audit import get_session_logs, get_all_logs
from ingest import build_vectorstore, get_vectorstore

app = FastAPI(title="Compliance Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    contract_name: str | None = None


class AnalysisResponse(BaseModel):
    session_id: str
    response: str
    legal_analysis: str
    validation: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(req: QueryRequest):
    result = analyze_contract(req.query, req.contract_name)
    return AnalysisResponse(**result)


@app.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    dest = os.path.join(CONTRACTS_DIR, file.filename)
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    # Rebuild vectorstore with new contract
    build_vectorstore()
    return {"message": f"Contract '{file.filename}' uploaded and indexed.", "filename": file.filename}


@app.get("/contracts")
def list_contracts():
    files = []
    for fname in os.listdir(CONTRACTS_DIR):
        if fname.endswith((".pdf", ".html", ".htm")):
            files.append(fname)
    return {"contracts": sorted(files)}


def extract_conclusion(text: str) -> str:
    """Extract only the conclusion section from the response."""
    patterns = [
        r'(?i)(?:#+\s*)?conclusion\s*[:.]?\s*\n([\s\S]*?)$',
        r'(?i)(?:#+\s*)?en conclusion\s*[:.,]?\s*([\s\S]*?)$',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    # Fallback: last paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if paragraphs:
        return paragraphs[-1]
    return text


def clean_text_for_tts(text: str) -> str:
    text = re.sub(r'\[Source:[^\]]*\]', '', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'---+', '', text)
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


@app.post("/tts")
def text_to_speech(req: QueryRequest):
    conclusion = extract_conclusion(req.query)
    clean_text = clean_text_for_tts(conclusion)
    if not clean_text:
        clean_text = clean_text_for_tts(req.query[:1000])
    tts = gTTS(text=clean_text, lang="fr")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return FileResponse(tmp.name, media_type="audio/mpeg", filename="response.mp3")


@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    import httpx

    audio_bytes = await file.read()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": (file.filename, audio_bytes, file.content_type)},
            data={"model": GROQ_WHISPER_MODEL, "language": "fr"},
            timeout=30.0,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Groq STT error: {resp.text}")
    return resp.json()


@app.get("/audit/{session_id}")
def get_audit(session_id: str):
    logs = get_session_logs(session_id)
    return {"logs": logs}


@app.get("/audit")
def get_all_audit(limit: int = 100):
    logs = get_all_logs(limit)
    return {"logs": logs}


@app.post("/reindex")
def reindex():
    build_vectorstore()
    return {"message": "Vectorstore rebuilt successfully."}
