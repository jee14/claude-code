# 자율 에이전트 시스템

![No Human Code](https://img.shields.io/badge/Human%20Code-0%25-red)
![AI Generated](https://img.shields.io/badge/AI%20Generated-100%25-green)
![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-Enabled-blue)

> 🎯 **Vibe Coding Project**: 개발자는 단지 "바이브"만 제시하고, AI 에이전트가 모든 코드를 작성합니다.
> 
> 이 프로젝트는 **프로덕션 코드를 전혀 보지 않고** 오직 AI 에이전트들의 협업만으로 완전한 애플리케이션을 구축하는 실험입니다.

## 🤔 바이브 코딩이란?

- 👨‍💻 **개발자**: "한국어 교정 도구 만들어줘" (바이브만 제시)
- 🤖 **Builder Agent**: 코드 작성 및 구현
- 🧐 **Evaluator Agent**: 코드 검토 및 개선 요구
- 🔄 **반복**: 목표 달성까지 자동으로 진행
- ✅ **결과**: 완성된 프로덕트 (개발자는 코드를 한 줄도 안 봄)

## 🚀 특징

- **Zero Human Code**: 인간이 작성한 프로덕션 코드 0%
- **Full Automation**: 설계부터 구현까지 완전 자동화
- **Multi-Agent Collaboration**: 여러 AI 에이전트의 협업
- **Workflow Support**: 복잡한 프로젝트도 단계별 자동 처리

---

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

### 단일 작업 실행

```bash
python main.py "FastAPI로 TODO API를 만들어주세요"
```

### 🆕 연속 작업 실행 (워크플로우)

워크플로우 매니저를 사용하여 여러 작업을 순차적으로 실행할 수 있습니다:

```bash
# 미리 정의된 워크플로우 실행
python workflow_manager.py tasks/korean_corrector_workflow.json

# 간단한 워크플로우 실행
python workflow_manager.py tasks/simple_workflow.json
```

#### 워크플로우 파일 형식

**간단한 형식** (작업 리스트):
```json
[
  "첫 번째 작업",
  "두 번째 작업",
  "세 번째 작업"
]
```

**구조화된 형식** (상세 설정):
```json
{
  "name": "워크플로우 이름",
  "description": "설명",
  "tasks": [
    {
      "name": "작업 이름",
      "task": "작업 내용"
    },
    ...
  ]
}
```

### 결과 확인

**단일 작업 결과**:
- `results/latest.json` - 가장 최근 결과
- `results/result_YYYYMMDD_HHMMSS.json` - 타임스탬프별 결과

**워크플로우 결과**:
- `results/workflows/workflow_YYYYMMDD_HHMMSS_final.json` - 전체 워크플로우 결과
- `results/workflows/workflow_YYYYMMDD_HHMMSS_state.json` - 진행 상태
- `results/workflows/latest_workflow.json` - 가장 최근 워크플로우

## 프로젝트 구조

```
auto-agent/
├── main.py              # 메인 실행 스크립트
├── workflow_manager.py  # 🆕 워크플로우 매니저
├── config.json          # 설정 파일
├── requirements.txt     # 의존성
├── .env                 # API 키 (gitignore)
├── tasks/              # 작업 정의
│   ├── example.json
│   ├── korean_corrector_workflow.json  # 🆕 한국어 교정 도구 개발
│   └── simple_workflow.json            # 🆕 간단한 예제
├── results/            # 실행 결과
│   └── workflows/      # 🆕 워크플로우 결과
└── logs/               # 로그 파일
```

## 설정 커스터마이징

`config.json` 파일에서 다음을 조정할 수 있습니다:

- `max_iterations`: 최대 반복 횟수 (기본: 10)
- `timeout_minutes`: 최대 실행 시간 (기본: 30분)
- `available_models`: 사용 가능한 모델 리스트
- `base_url`: OpenRouter API 엔드포인트
- 에이전트별 system message (Builder, Evaluator)
- `workflow_config`: 워크플로우 설정
  - `delay_between_tasks`: 작업 간 대기 시간 (초)
  - `save_intermediate_results`: 중간 결과 저장 여부
  - `continue_on_failure`: 실패 시 계속 진행 여부

## 예시

```bash
# 간단한 API 만들기
python main.py "Flask로 Hello World API 만들기"

# 복잡한 프로젝트
python main.py "Django + PostgreSQL로 블로그 시스템 만들기. 인증, CRUD, 검색 기능 포함"

# 🆕 워크플로우로 전체 프로젝트 개발
python workflow_manager.py tasks/korean_corrector_workflow.json
```

## 주의사항

- API 비용이 많이 들 수 있습니다 (반복 호출)
- 무한 루프를 방지하기 위해 max_iterations 설정 필수
- 결과가 항상 완벽하지 않을 수 있습니다
