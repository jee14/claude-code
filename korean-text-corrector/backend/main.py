"""
Korean Text Corrector Backend API
FastAPI server providing Korean text correction services
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

# Import correction engine
from correction_rules import KoreanCorrector, quick_correct, detailed_correct
from korean_spell_checker import KoreanSpellChecker
from openai_corrector import OpenAICorrector

app = FastAPI(
    title="Korean Text Corrector API",
    description="API for correcting Korean text spelling, spacing, and punctuation",
    version="2.0.0"
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

# Initialize correctors
corrector = KoreanCorrector()
spell_checker = KoreanSpellChecker()
openai_corrector = OpenAICorrector()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "Korean Text Corrector API is running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "All systems operational"
    }

@app.post("/correct", response_model=QuickCorrectionResponse)
async def correct_text(request: CorrectionRequest):
    """
    Quick text correction endpoint
    Returns corrected text without detailed analysis
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        corrected = quick_correct(request.text)
        
        return {
            "original": request.text,
            "corrected": corrected,
            "has_corrections": request.text != corrected
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction error: {str(e)}")

@app.post("/correct/detailed", response_model=DetailedCorrectionResponse)
async def correct_text_detailed(request: CorrectionRequest):
    """
    Detailed text correction endpoint using OpenAI GPT
    Returns corrected text with detailed analysis and correction log

    Modes:
    - proofreading: 맞춤법, 띄어쓰기, 문장부호 교정
    - copyediting: 문맥 일관성, 용어 통일, 중복 표현 검토
    - rewriting: 문장 구조 개선, 가독성 향상
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Use OpenAI corrector for reliable results
        analysis = openai_corrector.correct(request.text, request.mode)

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction error: {str(e)}")

@app.post("/analyze")
async def analyze_text(request: CorrectionRequest):
    """
    Analyze text and return detailed information
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        analysis = corrector.analyze_text(request.text)
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/rules/spelling")
async def get_spelling_rules():
    """Get all spelling correction rules"""
    return {
        "rules": corrector.rules.get_spelling_corrections(),
        "count": len(corrector.rules.get_spelling_corrections())
    }

@app.get("/rules/spacing")
async def get_spacing_rules():
    """Get all spacing pattern rules"""
    patterns = corrector.rules.get_spacing_patterns()
    return {
        "patterns": [{"pattern": p[0], "replacement": p[1]} for p in patterns],
        "count": len(patterns)
    }

@app.get("/rules/punctuation")
async def get_punctuation_rules():
    """Get all punctuation rules"""
    patterns = corrector.rules.get_punctuation_patterns()
    return {
        "patterns": [{"pattern": p[0], "replacement": p[1]} for p in patterns],
        "count": len(patterns)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
