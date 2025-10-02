# filename: create_correction_rules.py
import os

os.makedirs(os.path.dirname('../korean-text-corrector/backend/correction_rules.py'), exist_ok=True)

correction_rules_content = '''"""
Korean Text Correction Rules Module
Contains comprehensive rules for Korean spelling, spacing, and punctuation correction
"""

import re
from typing import List, Tuple, Dict

class CorrectionRules:
    """Korean text correction rules database"""
    
    # Common spelling mistakes
    SPELLING_RULES = {
        # 과거형 실수
        '됬어': '됐어',
        '됬다': '됐다',
        '됬는': '됐는',
        '됬을': '됐을',
        '됬지': '됐지',
        '했었': '했',
        '갔었': '갔',
        '왔었': '왔',
        
        # 어떻게/어떡해 구분
        '어떻해': '어떡해',
        '어떻해요': '어떡해요',
        '어떻하': '어떡하',
        '어떻하지': '어떡하지',
        '어떻하면': '어떡하면',
        
        # 안/않 구분
        '않돼': '안 돼',
        '않되': '안 돼',
        '않대': '안 돼',
        
        # 되/돼 구분
        '되요': '돼요',
        '되게': '되게',  # 올바른 형태
        '돼게': '되게',
        
        # -ㄹ게/-ㄹ께 구분
        '할께': '할게',
        '갈께': '갈게',
        '먹을께': '먹을게',
        '볼께': '볼게',
        
        # 만/밖에 구분
        '만큼': '만큼',
        '밖에': '밖에',
        
        # 기타 자주 틀리는 표현
        '왠지': '왠지',  # 올바름
        '웬지': '왠지',
        '금세': '금세',
        '금새': '금세',
        '일진': '일진',
        '일찐': '일진',
        '설레임': '설렘',
        '틀리다': '틀리다',  # 맥락에 따라 '다르다'
        '낳다': '낳다',  # 맥락에 따라 '낫다'
        
        # 띄어쓰기 관련
        '할수있': '할 수 있',
        '할수없': '할 수 없',
        '할수도': '할 수도',
        '그럼에도불구하고': '그럼에도 불구하고',
        '아무튼': '아무튼',
        '아무튼지': '아무튼',
    }
    
    # 띄어쓰기 패턴 규칙
    SPACING_PATTERNS = [
        # 조사는 붙여쓰기
        (r'(\w+)\s+(은|는|이|가|을|를|에|에서|로|으로|와|과|도|만|까지|부터|조차|마저|밖에|뿐|요)', r'\1\2'),
        
        # 보조용언은 띄어쓰기 (권장)
        (r'(\w+)(지다|하다|되다|싶다|있다|없다|같다|보다|만하다)', r'\1 \2'),
        
        # 의존명사는 띄어쓰기
        (r'(\w+)(것|수|지|줄|만큼|뿐|대로|채|바|체)', r'\1 \2'),
        
        # 단위명사는 띄어쓰기
        (r'(\d+)(개|명|마리|권|장|대|번|분|초|시간|일|년|월|원|달러)', r'\1 \2'),
        
        # 연결어미 뒤 띄어쓰기 확인
        (r'(\w+고)([가-힣])', r'\1 \2'),
        (r'(\w+지만)([가-힣])', r'\1 \2'),
        (r'(\w+어서|아서)([가-힣])', r'\1 \2'),
    ]
    
    # 문장부호 규칙
    PUNCTUATION_RULES = [
        # 마침표, 쉼표, 느낌표, 물음표 뒤 공백
        (r'([\.!?])([가-힣a-zA-Z])', r'\1 \2'),
        
        # 쉼표 뒤 공백
        (r'(,)([^\s])', r'\1 \2'),
        
        # 여러 공백을 하나로
        (r'\s{2,}', ' '),
        
        # 문장부호 앞 공백 제거
        (r'\s+([\.!?,;:])', r'\1'),
        
        # 괄호 안쪽 공백 제거
        (r'\(\s+', '('),
        (r'\s+\)', ')'),
        
        # 인용부호 처리
        (r'"\s+', '"'),
        (r'\s+"', '"'),
    ]
    
    # 맥락 기반 교정 패턴
    CONTEXTUAL_PATTERNS = {
        # "되다" vs "돼" 패턴
        'become_patterns': [
            (r'(\w+)되요', r'\1돼요'),
            (r'(\w+)되지', r'\1되지'),  # 부정문에서는 '되'
        ],
        
        # "틀리다" vs "다르다"
        'different_patterns': [
            (r'너무\s*틀려', '너무 달라'),
            (r'완전\s*틀려', '완전 달라'),
        ],
        
        # 존댓말 일관성
        'honorific_patterns': [
            (r'(\w+)요\.?\s+(\w+)다\.', r'\1요. \2요.'),
        ],
    }
    
    @staticmethod
    def get_spelling_corrections() -> Dict[str, str]:
        """Get spelling correction dictionary"""
        return CorrectionRules.SPELLING_RULES
    
    @staticmethod
    def get_spacing_patterns() -> List[Tuple[str, str]]:
        """Get spacing pattern rules"""
        return CorrectionRules.SPACING_PATTERNS
    
    @staticmethod
    def get_punctuation_patterns() -> List[Tuple[str, str]]:
        """Get punctuation pattern rules"""
        return CorrectionRules.PUNCTUATION_RULES
    
    @staticmethod
    def get_contextual_patterns() -> Dict[str, List[Tuple[str, str]]]:
        """Get contextual correction patterns"""
        return CorrectionRules.CONTEXTUAL_PATTERNS


class KoreanCorrector:
    """Korean text corrector using predefined rules"""
    
    def __init__(self):
        self.rules = CorrectionRules()
        self.corrections_made = []
    
    def correct_spelling(self, text: str) -> str:
        """Apply spelling corrections"""
        corrected = text
        spelling_rules = self.rules.get_spelling_corrections()
        
        for wrong, correct in spelling_rules.items():
            if wrong in corrected:
                corrected = corrected.replace(wrong, correct)
                self.corrections_made.append({
                    'type': 'spelling',
                    'original': wrong,
                    'corrected': correct
                })
        
        return corrected
    
    def correct_spacing(self, text: str) -> str:
        """Apply spacing corrections"""
        corrected = text
        spacing_patterns = self.rules.get_spacing_patterns()
        
        for pattern, replacement in spacing_patterns:
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected
    
    def correct_punctuation(self, text: str) -> str:
        """Apply punctuation corrections"""
        corrected = text
        punctuation_patterns = self.rules.get_punctuation_patterns()
        
        for pattern, replacement in punctuation_patterns:
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected
    
    def correct_contextual(self, text: str) -> str:
        """Apply contextual corrections"""
        corrected = text
        contextual_patterns = self.rules.get_contextual_patterns()
        
        for category, patterns in contextual_patterns.items():
            for pattern, replacement in patterns:
                corrected = re.sub(pattern, replacement, corrected)
        
        return corrected
    
    def correct_all(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply all corrections and return corrected text with change log"""
        self.corrections_made = []
        
        # Apply corrections in order
        corrected = text
        corrected = self.correct_spelling(corrected)
        corrected = self.correct_spacing(corrected)
        corrected = self.correct_contextual(corrected)
        corrected = self.correct_punctuation(corrected)
        
        return corrected, self.corrections_made
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text and provide detailed corrections"""
        original_text = text
        corrected_text, corrections = self.correct_all(text)
        
        analysis = {
            'original': original_text,
            'corrected': corrected_text,
            'has_corrections': original_text != corrected_text,
            'corrections': corrections,
            'statistics': {
                'original_length': len(original_text),
                'corrected_length': len(corrected_text),
                'num_corrections': len(corrections)
            }
        }
        
        return analysis


# Utility functions for external use
def quick_correct(text: str) -> str:
    """Quick correction without detailed analysis"""
    corrector = KoreanCorrector()
    corrected, _ = corrector.correct_all(text)
    return corrected


def detailed_correct(text: str) -> Dict:
    """Detailed correction with analysis"""
    corrector = KoreanCorrector()
    return corrector.analyze_text(text)
'''

with open('../korean-text-corrector/backend/correction_rules.py', 'w', encoding='utf-8') as f:
    f.write(correction_rules_content)

print('Created: ../korean-text-corrector/backend/correction_rules.py')