"""
Naver Spell Checker using dynamic passportKey extraction
GitHub Issue #48 기반 구현
"""
import re
import requests
from typing import Dict, List


class NaverCorrector:
    """네이버 맞춤법 검사기"""

    def __init__(self):
        self.base_url = "https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy"
        self.passport_key = None

    def get_passport_key(self) -> str:
        """네이버 검색 페이지에서 passportKey 추출"""
        try:
            url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=네이버+맞춤법+검사기"
            res = requests.get(url, timeout=10)
            match = re.search(r'passportKey=([^&"}\]]+)', res.text)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            print(f"PassportKey 추출 실패: {e}")
            return None

    def correct(self, text: str, mode: str = "proofreading") -> Dict:
        """
        텍스트 교정 실행

        Args:
            text: 교정할 텍스트 (최대 500자)
            mode: 교정 모드 (proofreading만 지원)

        Returns:
            Dict with 'original', 'corrected', 'corrections' keys
        """
        # passportKey 가져오기 (캐시되지 않았으면 새로 추출)
        if not self.passport_key:
            self.passport_key = self.get_passport_key()

        if not self.passport_key:
            return self._fallback_result(text, "PassportKey를 가져올 수 없습니다")

        try:
            # 500자 제한
            if len(text) > 500:
                text = text[:500]

            payload = {
                "passportKey": self.passport_key,
                'color_blindness': '0',
                'q': text
            }

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'referer': 'https://search.naver.com/'
            }

            response = requests.get(self.base_url, params=payload, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            print(f"API Response: {result}")  # 디버깅용

            # 응답 파싱
            if 'message' in result and 'error' in result['message']:
                # passportKey가 만료되었을 수 있으므로 재시도
                self.passport_key = self.get_passport_key()
                if self.passport_key:
                    payload['passportKey'] = self.passport_key
                    response = requests.get(self.base_url, params=payload, headers=headers, timeout=10)
                    result = response.json()
                    print(f"API Response (retry): {result}")  # 디버깅용
                else:
                    return self._fallback_result(text, "PassportKey 갱신 실패")

            # 교정 결과 추출
            corrections = []
            corrected_text = text

            if 'message' in result and 'result' in result['message']:
                result_data = result['message']['result']
                errata_count = result_data.get('errata_count', 0)

                # notag_html에 교정된 텍스트가 있음
                if errata_count > 0 and 'notag_html' in result_data:
                    corrected_text = result_data['notag_html']

                    # HTML에서 개별 교정 항목 추출 (origin_html과 html 비교)
                    # 일단 전체 교정만 제공 (개별 교정 내역은 HTML 파싱 필요)
                    corrections.append({
                        'type': 'spelling',
                        'original': text,
                        'corrected': corrected_text,
                        'explanation': f'{errata_count}개 교정됨'
                    })

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

        except Exception as e:
            print(f"Naver API Error: {e}")
            return self._fallback_result(text, str(e))

    def _fallback_result(self, text: str, error_msg: str = "API 오류") -> Dict:
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
    corrector = NaverCorrector()

    test_cases = [
        "안녕하세요? 됬는지 확인해볼게욬ㅋ",
        "확인하고있어요",
        "할수있어요",
    ]

    for text in test_cases:
        print(f"\n{'='*60}")
        print(f"원본: {text}")
        result = corrector.correct(text)
        print(f"교정: {result['corrected']}")
        if result.get('error'):
            print(f"에러: {result['error']}")
        else:
            print(f"변경 개수: {len(result['corrections'])}")
            for corr in result['corrections']:
                print(f"  - {corr['original']} → {corr['corrected']}")
                print(f"    설명: {corr['explanation']}")
