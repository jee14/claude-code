"""
한국어 문장 다듬기 Backend API
FastAPI server providing Korean text refinement services using OpenRouter API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict
import uvicorn

# Import correction engines
from openai_corrector import OpenAICorrector
from naver_corrector import NaverCorrector

app = FastAPI(
    title="한국어 문장 다듬기 API",
    description="API for refining Korean text using Naver + OpenRouter",
    version="3.1.0"
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

    @validator('text')
    def validate_text_length(cls, v):
        if len(v) > 1000:
            raise ValueError('Text must not exceed 1000 characters')
        return v

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
openai_corrector = OpenAICorrector()
naver_corrector = NaverCorrector()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "version": "3.1.0",
        "message": "한국어 문장 다듬기 API (Naver + OpenRouter)"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.1.0",
        "message": "한국어 문장 다듬기 - Naver + OpenRouter API operational"
    }

@app.post("/correct", response_model=DetailedCorrectionResponse)
async def correct_text(request: CorrectionRequest):
    """
    Text correction endpoint with sequential processing

    Modes:
    - proofreading: 교정만 수행 (Naver API)
    - copyediting: 교정 → 교열 순차 수행 (Naver → OpenRouter)
    - rewriting: 교정 → 교열 → 윤문 순차 수행 (Naver → OpenRouter → OpenRouter)
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        print(f"[DEBUG] 받은 원본 텍스트: {request.text}")
        print(f"[DEBUG] request.text repr: {repr(request.text)}")
        current_text = request.text
        all_corrections = []

        # 1단계: 교정 (proofreading) - 모든 모드에서 실행
        print(f"[1단계] 교정 시작: {current_text}")
        proofreading_result = naver_corrector.correct(current_text, "proofreading")
        if 'error' in proofreading_result:
            print(f"Naver API 실패, OpenRouter로 폴백: {proofreading_result['error']}")
            proofreading_result = openai_corrector.correct(current_text, "proofreading")

        current_text = proofreading_result['corrected']
        all_corrections.extend(proofreading_result.get('corrections', []))
        print(f"[1단계] 교정 완료: {current_text}")

        # proofreading 모드면 여기서 종료
        if request.mode == "proofreading":
            return proofreading_result

        # 2단계: 교열 (copyediting) - copyediting, rewriting 모드에서 실행
        print(f"[2단계] 교열 시작: {current_text}")
        copyediting_result = openai_corrector.correct(current_text, "copyediting")
        current_text = copyediting_result['corrected']
        all_corrections.extend(copyediting_result.get('corrections', []))
        print(f"[2단계] 교열 완료: {current_text}")

        # copyediting 모드면 여기서 종료
        if request.mode == "copyediting":
            return {
                'original': request.text,
                'corrected': current_text,
                'has_corrections': len(all_corrections) > 0,
                'corrections': all_corrections,
                'statistics': {
                    'original_length': len(request.text),
                    'corrected_length': len(current_text),
                    'num_corrections': len(all_corrections)
                }
            }

        # 3단계: 윤문 (rewriting) - rewriting 모드에서만 실행
        print(f"[3단계] 윤문 시작: {current_text}")
        rewriting_result = openai_corrector.correct(current_text, "rewriting")
        current_text = rewriting_result['corrected']
        all_corrections.extend(rewriting_result.get('corrections', []))
        print(f"[3단계] 윤문 완료: {current_text}")

        final_response = {
            'original': request.text,
            'corrected': current_text,
            'has_corrections': len(all_corrections) > 0,
            'corrections': all_corrections,
            'statistics': {
                'original_length': len(request.text),
                'corrected_length': len(current_text),
                'num_corrections': len(all_corrections)
            }
        }
        print(f"[DEBUG] 최종 응답: original={final_response['original']}, corrected={final_response['corrected']}")
        import json
        print(f"[DEBUG] JSON 직렬화: {json.dumps(final_response, ensure_ascii=False)}")
        return final_response

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
