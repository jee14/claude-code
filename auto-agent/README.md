# 자율 에이전트 시스템

Builder와 Evaluator 에이전트가 서로 대화하며 자동으로 프로젝트를 완성하는 시스템입니다.

## 작동 원리

1. **Builder 에이전트**: 코드를 작성하고 개선
2. **Evaluator 에이전트**: 코드를 평가하고 피드백 제공
3. 두 에이전트가 자동으로 대화하며 목표 달성까지 반복
4. Evaluator가 "APPROVE"를 하면 종료

## 설치

```bash
pip install -r requirements.txt
```

## 설정

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. OpenRouter API 키와 모델 설정:
```bash
# OpenRouter API 키 (https://openrouter.ai/keys 에서 발급)
OPENROUTER_API_KEY=sk-or-v1-...

# 사용할 모델 선택
OPENROUTER_MODEL=anthropic/claude-sonnet-4.5
```

### 사용 가능한 모델

- `x-ai/grok-code-fast-1` - X.AI Grok (코드 특화, 빠름)
- `openai/gpt-5` - OpenAI GPT-5
- `google/gemini-2.5-pro` - Google Gemini Pro
- `anthropic/claude-sonnet-4.5` - Anthropic Claude Sonnet (추천)
- `deepseek/deepseek-chat-v3.1:free` - DeepSeek (무료)

## 사용법

### 직접 실행

```bash
python main.py "FastAPI로 TODO API를 만들어주세요"
```

### 결과 확인

- 결과는 `results/` 디렉토리에 저장됨
- `results/latest.json` - 가장 최근 결과
- `results/result_YYYYMMDD_HHMMSS.json` - 타임스탬프별 결과

## 프로젝트 구조

```
auto-agent/
├── main.py              # 메인 실행 스크립트
├── config.json          # 설정 파일
├── requirements.txt     # 의존성
├── .env                 # API 키 (gitignore)
├── tasks/              # 작업 정의
│   └── example.json
├── results/            # 실행 결과
└── logs/               # 로그 파일
```

## 설정 커스터마이징

`config.json` 파일에서 다음을 조정할 수 있습니다:

- `max_iterations`: 최대 반복 횟수 (기본: 10)
- `timeout_minutes`: 최대 실행 시간 (기본: 30분)
- `available_models`: 사용 가능한 모델 리스트
- `base_url`: OpenRouter API 엔드포인트
- 에이전트별 system message (Builder, Evaluator)

## 예시

```bash
# 간단한 API 만들기
python main.py "Flask로 Hello World API 만들기"

# 복잡한 프로젝트
python main.py "Django + PostgreSQL로 블로그 시스템 만들기. 인증, CRUD, 검색 기능 포함"
```

## 주의사항

- API 비용이 많이 들 수 있습니다 (반복 호출)
- 무한 루프를 방지하기 위해 max_iterations 설정 필수
- 결과가 항상 완벽하지 않을 수 있습니다
