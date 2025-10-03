# 한국어 문장 다듬기 - Backend

## 프로젝트 개요
한국어 텍스트를 다듬어주는 웹 애플리케이션의 백엔드 API입니다. 교정(맞춤법/띄어쓰기), 교열(일관성/중복), 윤문(문장 구조 개선) 기능을 제공합니다.

## 개발 원칙

### 코드 품질
- Python 코드는 ruff로 자동 포맷팅
- Type hints 적극 사용
- 간결하고 명확한 코드 작성
- 불필요한 중복 제거

### API 설계
- RESTful 원칙 준수
- 명확한 에러 메시지
- UTF-8 인코딩 사용
- CORS 적절히 설정

### 커밋 규칙
- 모든 테스트 통과 후 커밋
- 의미 있는 커밋 메시지 작성
- 기능별로 작은 단위로 커밋

## 주요 기능

### 1. 교정 (Proofreading)
- 네이버 맞춤법 검사 API 사용
- 동적 passportKey 추출로 API 차단 우회
- 맞춤법, 띄어쓰기, 문장부호 자동 교정
- 실패 시 OpenRouter로 자동 폴백

### 2. 교열 (Copy Editing)
- 교정 후 OpenRouter API로 교열 수행
- 문맥 일관성, 용어 통일, 중복 표현 검토
- Claude Sonnet 4.5 모델 사용

### 3. 윤문 (Rewriting)
- 교정 → 교열 후 윤문 수행
- 문장 구조 개선, 가독성 향상
- 자연스러운 한국어 표현 제안

## 기술 스택
- **Framework**: FastAPI 0.104.1
- **Python**: 3.12
- **AI APIs**:
  - 네이버 맞춤법 검사 API (교정)
  - OpenRouter API (Claude Sonnet 4.5) (교열, 윤문)

## 순차 처리 로직
```
교정 버튼: 교정만
교열 버튼: 교정 → 교열
윤문 버튼: 교정 → 교열 → 윤문
```

## Claude Code 설정

### Hooks
- **PreToolUse**: 파일 수정 전 Python 구문 검사
- **PostToolUse**: 파일 수정 후 ruff 자동 포맷팅 및 lint

설정 파일: `.claude/settings.json`

## API 엔드포인트

### POST /correct
텍스트 교정/교열/윤문 수행

**Request:**
```json
{
  "text": "교정할 텍스트 (최대 1000자)",
  "mode": "proofreading|copyediting|rewriting"
}
```

**Response:**
```json
{
  "original": "원본 텍스트",
  "corrected": "교정된 텍스트",
  "has_corrections": true,
  "corrections": [
    {
      "type": "spelling",
      "original": "틀린 표현",
      "corrected": "올바른 표현",
      "explanation": "설명"
    }
  ],
  "statistics": {
    "original_length": 100,
    "corrected_length": 102,
    "num_corrections": 3
  }
}
```

## 환경 변수
```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4.5
```

## 실행 방법
```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py

# 또는 환경변수와 함께
OPENROUTER_API_KEY=your-key python main.py
```

서버는 `http://localhost:8000`에서 실행됩니다.
