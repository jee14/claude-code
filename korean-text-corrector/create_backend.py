# filename: create_backend.py
import os

# Create backend directory
os.makedirs('../korean-text-corrector/backend', exist_ok=True)

# Main FastAPI application code
main_py_content = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import re

app = FastAPI(title="Korean Text Corrector API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CorrectionRequest(BaseModel):
    text: str
    mode: Literal['proofreading', 'copyediting', 'rewriting']

class Position(BaseModel):
    start: int
    end: int

class Correction(BaseModel):
    type: str
    original: str
    corrected: str
    explanation: str
    position: Position

class CorrectionResponse(BaseModel):
    original: str
    corrected: str
    corrections: List[Correction]

# Rule-based correction patterns
class KoreanCorrector:
    def __init__(self):
        # Common Korean spelling errors and corrections
        self.spelling_rules = {
            # Double consonants
            '갔다': '갔다',
            '됬다': '됐다',
            '했는데': '했는데',
            '되요': '돼요',
            '되': '돼',
            '왠지': '웬지',
            '웬일': '왠일',
            
            # Common mistakes
            '않되': '안 되',
            '안됩니다': '안 됩니다',
            '않습니다': '않습니다',
            '할려고': '하려고',
            '할꺼': '할 거',
            '할께요': '할게요',
            '할수있': '할 수 있',
            '할수없': '할 수 없',
            '이따가': '있다가',
            '그러니까': '그러니까',
            '그런데': '그런데',
        }
        
        # Spacing rules (common compounds that need spacing)
        self.spacing_rules = [
            (r'할수있', '할 수 있'),
            (r'할수없', '할 수 없'),
            (r'할수도', '할 수도'),
            (r'될수있', '될 수 있'),
            (r'될수없', '될 수 없'),
            (r'하는것', '하는 것'),
            (r'하는게', '하는 게'),
            (r'인것같', '인 것 같'),
            (r'하고싶', '하고 싶'),
            (r'보고싶', '보고 싶'),
        ]
        
        # Punctuation rules
        self.punctuation_rules = [
            (r'([^\.])(\s*)$', r'\\1.'),  # Add period at end
            (r'\s+([,\.!?])', r'\\1'),  # Remove space before punctuation
            (r'([,\.!?])([가-힣a-zA-Z])', r'\\1 \\2'),  # Add space after punctuation
            (r'\.\.+', '.'),  # Multiple periods to single
            (r'\!\!+', '!'),  # Multiple exclamations to single
            (r'\?\?+', '?'),  # Multiple questions to single
        ]
    
    def find_corrections(self, text: str, mode: str) -> List[Correction]:
        corrections = []
        current_text = text
        
        if mode in ['proofreading', 'copyediting']:
            # Apply spelling corrections
            for wrong, right in self.spelling_rules.items():
                for match in re.finditer(re.escape(wrong), current_text):
                    corrections.append(Correction(
                        type='spelling',
                        original=wrong,
                        corrected=right,
                        explanation=f'"{wrong}"은(는) 올바른 맞춤법이 아닙니다. "{right}"(으)로 수정합니다.',
                        position=Position(start=match.start(), end=match.end())
                    ))
            
            # Apply spacing corrections
            for pattern, replacement in self.spacing_rules:
                for match in re.finditer(pattern, current_text):
                    original = match.group(0)
                    corrections.append(Correction(
                        type='spacing',
                        original=original,
                        corrected=replacement,
                        explanation=f'띄어쓰기가 필요합니다. "{original}"을(를) "{replacement}"(으)로 수정합니다.',
                        position=Position(start=match.start(), end=match.end())
                    ))
        
        if mode in ['copyediting', 'rewriting']:
            # Apply punctuation corrections
            for pattern, replacement in self.punctuation_rules:
                matches = list(re.finditer(pattern, current_text))
                for match in matches:
                    original = match.group(0)
                    corrected = re.sub(pattern, replacement, original)
                    if original != corrected:
                        corrections.append(Correction(
                            type='punctuation',
                            original=original,
                            corrected=corrected,
                            explanation='문장부호를 수정합니다.',
                            position=Position(start=match.start(), end=match.end())
                        ))
        
        if mode == 'rewriting':
            # Check for repetitive words
            words = re.findall(r'[가-힣]+', current_text)
            for i in range(len(words) - 1):
                if words[i] == words[i + 1] and len(words[i]) > 1:
                    # Find position of repeated word
                    pattern = re.escape(words[i]) + r'\\s+' + re.escape(words[i])
                    for match in re.finditer(pattern, current_text):
                        corrections.append(Correction(
                            type='style',
                            original=match.group(0),
                            corrected=words[i],
                            explanation=f'중복된 단어 "{words[i]}"을(를) 제거합니다.',
                            position=Position(start=match.start(), end=match.end())
                        ))
        
        return corrections
    
    def apply_corrections(self, text: str, corrections: List[Correction]) -> str:
        # Sort corrections by position (reverse order to maintain positions)
        sorted_corrections = sorted(corrections, key=lambda x: x.position.start, reverse=True)
        
        corrected_text = text
        for correction in sorted_corrections:
            start = correction.position.start
            end = correction.position.end
            corrected_text = corrected_text[:start] + correction.corrected + corrected_text[end:]
        
        return corrected_text

corrector = KoreanCorrector()

@app.get("/")
async def root():
    return {
        "message": "Korean Text Corrector API",
        "version": "1.0.0",
        "endpoints": {
            "correct": "/api/correct"
        }
    }

@app.post("/api/correct", response_model=CorrectionResponse)
async def correct_text(request: CorrectionRequest):
    """
    Correct Korean text based on the specified mode.
    
    Modes:
    - proofreading: Basic spelling and spacing corrections
    - copyediting: Spelling, spacing, and punctuation corrections
    - rewriting: All corrections plus style improvements
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Find all corrections
        corrections = corrector.find_corrections(request.text, request.mode)
        
        # Apply corrections to get corrected text
        corrected_text = corrector.apply_corrections(request.text, corrections)
        
        return CorrectionResponse(
            original=request.text,
            corrected=corrected_text,
            corrections=corrections
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# Write the main.py file
with open('../korean-text-corrector/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(main_py_content)

print('Created: ../korean-text-corrector/backend/main.py')

# Create requirements.txt
requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
'''

with open('../korean-text-corrector/backend/requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content)

print('Created: ../korean-text-corrector/backend/requirements.txt')

# Create README for backend
readme_content = '''# Korean Text Corrector - Backend API

FastAPI-based backend for Korean text correction.

## Features

- **POST /api/correct**: Main correction endpoint
- **GET /**: API information
- **GET /health**: Health check endpoint

## Correction Modes

1. **proofreading**: Basic spelling and spacing corrections
2. **copyediting**: Spelling, spacing, and punctuation corrections
3. **rewriting**: All corrections plus style improvements

## Installation
