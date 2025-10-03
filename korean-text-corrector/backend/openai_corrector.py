"""
Korean Text Corrector using OpenRouter API
OpenRouter API를 사용한 한국어 교정 (Claude 등 다양한 모델 지원)
"""
import os
from typing import Dict, List
import json


class OpenAICorrector:
    """OpenRouter API를 사용한 한국어 교정"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5")

        if not self.api_key:
            print("Warning: OPENROUTER_API_KEY not set. Corrector will not work.")

    def correct(self, text: str, mode: str = "proofreading") -> Dict:
        """
        텍스트 교정 실행

        Args:
            text: 교정할 텍스트
            mode: 교정 모드 (proofreading, copyediting, rewriting)

        Returns:
            Dict with 'original', 'corrected', 'corrections' keys
        """
        if not self.api_key:
            return self._fallback_result(text)

        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            # 모드별 프롬프트
            prompts = {
                "proofreading": """다음 한국어 텍스트의 맞춤법, 띄어쓰기, 문장부호를 교정해주세요.

띄어쓰기 규칙을 반드시 적용하세요:
- 보조 용언은 띄어쓰기: "하고있어요" → "하고 있어요", "하지않아요" → "하지 않아요"
- 의존 명사는 띄어쓰기: "할수있어요" → "할 수 있어요", "할수도" → "할 수도"
- 단위 명사는 띄어쓰기: "10개" → "10 개", "3시간" → "3 시간"

입력 텍스트:
{text}

출력 형식:
{{
  "corrected": "교정된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "spelling|spacing|punctuation", "explanation": "설명"}}
  ]
}}""",
                "copyediting": """다음 한국어 텍스트를 교열해주세요. 문맥 일관성, 용어 통일, 중복 표현을 검토하고 개선해주세요.

입력 텍스트:
{text}

출력 형식:
{{
  "corrected": "교열된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "consistency|terminology|redundancy", "explanation": "설명"}}
  ]
}}""",
                "rewriting": """다음 한국어 텍스트를 윤문해주세요. 문장 구조를 개선하고 가독성을 향상시켜주세요.

입력 텍스트:
{text}

출력 형식:
{{
  "corrected": "윤문된 전체 텍스트",
  "changes": [
    {{"original": "원본", "corrected": "수정본", "type": "structure|clarity|style", "explanation": "설명"}}
  ]
}}"""
            }

            prompt = prompts.get(mode, prompts["proofreading"]).format(text=text)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전문 한국어 교정자입니다. 정확하고 자연스러운 한국어로 교정해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # JSON 추출 (```json ... ``` 형식일 수 있음)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # 응답 형식 변환
            corrections = []
            for change in result.get("changes", []):
                corrections.append({
                    'type': change.get('type', 'spelling'),
                    'original': change.get('original', ''),
                    'corrected': change.get('corrected', ''),
                    'explanation': change.get('explanation', '')
                })

            return {
                'original': text,
                'corrected': result.get('corrected', text),
                'has_corrections': len(corrections) > 0,
                'corrections': corrections,
                'statistics': {
                    'original_length': len(text),
                    'corrected_length': len(result.get('corrected', text)),
                    'num_corrections': len(corrections)
                }
            }

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return self._fallback_result(text, str(e))

    def _fallback_result(self, text: str, error_msg: str = "OpenRouter API key not configured") -> Dict:
        """API 사용 불가시 fallback"""
        return {
            'original': text,
            'corrected': text,
            'has_corrections': False,
            'corrections': [],
            'error': error_msg,
            'statistics': {
                'original_length': len(text),
                'corrected_length': len(text),
                'num_corrections': 0
            }
        }


# 테스트 코드
if __name__ == "__main__":
    corrector = OpenAICorrector()

    test_cases = [
        ("안녕하세요? 됬는지 확인해볼게욬ㅋ", "proofreading"),
        ("좋아요 좋아요 정말 좋아요", "copyediting"),
        ("이거는 그냥 간단하게 말하자면 좀 복잡하게 표현한 것", "rewriting"),
    ]

    for text, mode in test_cases:
        print(f"\n{'='*60}")
        print(f"모드: {mode}")
        print(f"원본: {text}")
        result = corrector.correct(text, mode)
        print(f"교정: {result['corrected']}")
        if result.get('error'):
            print(f"에러: {result['error']}")
        else:
            print(f"변경 개수: {len(result['corrections'])}")
            for corr in result['corrections']:
                print(f"  - {corr['original']} → {corr['corrected']} ({corr['type']})")
