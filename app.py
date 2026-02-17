import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

# Import your existing logic
from rag.settings import apply_settings
from rag.query_engine import query_civicai

app = FastAPI()

# --- THE CORS FIX ---
# This allows your GitHub Pages site to talk to Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development. Change to your specific github.io URL later.
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize settings once when the server starts
apply_settings()

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DEFAULT_BASE = PROJECT_ROOT / "storage" / "index"

class Question(BaseModel):
    query: str
    format: str = "pdf" # default to pdf

@app.get("/")
def health_check():
    return {"status": "online", "message": "CivicAI API is running"}

@app.post("/ask")
def ask_question(item: Question):
    index_path = Path(DEFAULT_BASE, item.format)
    
    # Run your RAG logic
    result = query_civicai(item.query, index_path)
    
    return {
        "query": item.query,
        "answer": str(result),
        "sources": [n.get_text() for n in result.source_nodes] if hasattr(result, 'source_nodes') else []
    }
