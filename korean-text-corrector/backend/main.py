"""
Korean Text Corrector Backend API
FastAPI server providing Korean text correction services using OpenRouter API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

# Import correction engine
from openai_corrector import OpenAICorrector

app = FastAPI(
    title="Korean Text Corrector API",
    description="API for correcting Korean text using OpenRouter (Claude, GPT, etc.)",
    version="3.0.0"
)

# Configure JSON response to use UTF-8 encoding with ensure_ascii=False
from fastapi.responses import JSONResponse
import json

class UTF8JSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

app.default_response_class = UTF8JSONResponse

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class CorrectionRequest(BaseModel):
    text: str
    detailed: Optional[bool] = False
    mode: Optional[str] = "proofreading"  # proofreading, copyediting, rewriting

class QuickCorrectionResponse(BaseModel):
    original: str
    corrected: str
    has_corrections: bool

class DetailedCorrectionResponse(BaseModel):
    original: str
    corrected: str
    has_corrections: bool
    corrections: List[Dict]
    statistics: Dict

class HealthResponse(BaseModel):
    status: str
    version: str
    message: str

# Initialize OpenRouter corrector
openai_corrector = OpenAICorrector()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "message": "Korean Text Corrector API (OpenRouter)"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "message": "OpenRouter API operational"
    }

@app.post("/correct", response_model=DetailedCorrectionResponse)
async def correct_text(request: CorrectionRequest):
    """
    Text correction endpoint using OpenRouter API
    Returns corrected text with detailed analysis

    Modes:
    - proofreading: 맞춤법, 띄어쓰기, 문장부호 교정
    - copyediting: 문맥 일관성, 용어 통일, 중복 표현 검토
    - rewriting: 문장 구조 개선, 가독성 향상
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Use OpenRouter for all corrections
        analysis = openai_corrector.correct(request.text, request.mode)

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction error: {str(e)}")

@app.post("/correct/detailed", response_model=DetailedCorrectionResponse)
async def correct_text_detailed(request: CorrectionRequest):
    """
    Alias for /correct endpoint (for backward compatibility)
    """
    return await correct_text(request)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
