"""
Langfuse 프롬프트 설정 스크립트
korean-text-refiner 프롬프트를 3가지 label로 생성합니다.
"""
import os
from langfuse import Langfuse

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

# Langfuse 클라이언트 초기화
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# 프롬프트 설정
prompts = [
    {
        "name": "korean-text-proofreading",
        "prompt": """다음 한국어 텍스트의 맞춤법, 띄어쓰기, 문장부호를 교정해주세요.

띄어쓰기 규칙을 반드시 적용하세요:
- 보조 용언은 띄어쓰기: "하고있어요" → "하고 있어요", "하지않아요" → "하지 않아요"
- 의존 명사는 띄어쓰기: "할수있어요" → "할 수 있어요", "할수도" → "할 수도"
- 단위 명사는 띄어쓰기: "10개" → "10 개", "3시간" → "3 시간"

입력 텍스트:
{{text}}

출력 형식:
{{
  "corrected": "교정된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "spelling|spacing|punctuation", "explanation": "설명"}}
  ]
}}""",
        "config": {
            "system_message": "당신은 전문 한국어 맞춤법 교정 전문가입니다. 정확하고 자연스러운 한국어로 교정해주세요."
        }
    },
    {
        "name": "korean-text-copyediting",
        "prompt": """다음 한국어 텍스트를 교열해주세요. 문맥 일관성, 용어 통일, 중복 표현을 검토하고 개선해주세요.

입력 텍스트:
{{text}}

출력 형식:
{{
  "corrected": "교열된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "consistency|terminology|redundancy", "explanation": "설명"}}
  ]
}}""",
        "config": {
            "system_message": "당신은 전문 한국어 교열 전문가입니다. 문맥의 일관성을 유지하며 자연스러운 한국어로 다듬어주세요."
        }
    },
    {
        "name": "korean-text-rewriting",
        "prompt": """다음 한국어 텍스트를 윤문해주세요. 문장 구조를 개선하고 가독성을 향상시켜주세요.

입력 텍스트:
{{text}}

출력 형식:
{{
  "corrected": "윤문된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "structure|clarity|style", "explanation": "설명"}}
  ]
}}""",
        "config": {
            "system_message": "당신은 전문 한국어 윤문 전문가입니다. 문장 구조를 개선하고 가독성을 높여주세요."
        }
    }
]

# 프롬프트 생성
print("🚀 Langfuse 프롬프트 생성 중...")
for prompt_data in prompts:
    try:
        result = langfuse.create_prompt(
            name=prompt_data["name"],
            prompt=prompt_data["prompt"],
            config=prompt_data["config"]
        )
        print(f"✅ {prompt_data['name']} 프롬프트 생성 완료!")
    except Exception as e:
        print(f"❌ {prompt_data['name']} 프롬프트 생성 실패: {e}")

print("\n✨ 완료! Langfuse 대시보드에서 프롬프트를 확인하세요.")
print("📍 https://cloud.langfuse.com/project/cmgaq35ni06pxad074yibta8g/prompts")
