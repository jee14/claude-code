"""
Korean Spell Checker using Pusan National University API
부산대학교 한국어 맞춤법 검사기 API 활용
"""
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class KoreanSpellChecker:
    """부산대 맞춤법 검사기를 사용한 한국어 교정"""

    def __init__(self):
        self.api_url = "http://speller.cs.pusan.ac.kr/results"

    def check(self, text: str) -> Dict:
        """
        맞춤법 검사 실행

        Args:
            text: 검사할 텍스트

        Returns:
            Dict with 'original', 'corrected', 'corrections' keys
        """
        try:
            # API 호출
            response = requests.post(
                self.api_url,
                data={'text1': text},
                timeout=10
            )

            if response.status_code != 200:
                return self._error_result(text, "API 호출 실패")

            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 교정 결과 추출
            corrections = []
            corrected_text = text

            # 오류가 있는 단어 찾기
            error_words = soup.find_all('span', {'class': 'error'})

            for error in error_words:
                original_word = error.get_text()

                # 제안 단어 찾기
                suggestion = error.find_next('span', {'class': 'green'})
                if suggestion:
                    corrected_word = suggestion.get_text()

                    corrections.append({
                        'type': 'spelling',
                        'original': original_word,
                        'corrected': corrected_word,
                        'explanation': f'{original_word} → {corrected_word}'
                    })

                    # 텍스트 교정
                    corrected_text = corrected_text.replace(original_word, corrected_word, 1)

            return {
                'original': text,
                'corrected': corrected_text,
                'has_corrections': len(corrections) > 0,
                'corrections': corrections,
                'statistics': {
                    'original_length': len(text),
                    'corrected_length': len(corrected_text),
                    'num_corrections': len(corrections)
                }
            }

        except requests.Timeout:
            return self._error_result(text, "API 타임아웃")
        except Exception as e:
            return self._error_result(text, f"오류: {str(e)}")

    def _error_result(self, text: str, error_msg: str) -> Dict:
        """에러 발생 시 기본 결과 반환"""
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
    checker = KoreanSpellChecker()

    test_cases = [
        "안녕하세요? 저는 이거 한 번 해보렵니다.",
        "됬다 할수있어요",
        "어떻해요 이거",
    ]

    for text in test_cases:
        print(f"\n원본: {text}")
        result = checker.check(text)
        print(f"교정: {result['corrected']}")
        print(f"수정 개수: {result['statistics']['num_corrections']}")
        if result['corrections']:
            for corr in result['corrections']:
                print(f"  - {corr['original']} → {corr['corrected']}")
