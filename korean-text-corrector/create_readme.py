# filename: create_readme.py
import os

readme_content = '''# Korean Text Corrector - Backend

## Features

### Spelling Correction
- 과거형 실수: 됬어 → 됐어
- 어떻게/어떡해 구분
- 안/않 구분
- 되/돼 구분
- -ㄹ게/-ㄹ께 구분
- 기타 자주 틀리는 표현 (왠지/웬지, 금세/금새 등)

### Spacing Rules
- 조사 붙여쓰기
- 보조용언 띄어쓰기
- 의존명사 띄어쓰기
- 단위명사 띄어쓰기

### Punctuation
- 문장부호 뒤 공백
- 괄호/인용부호 처리
- 중복 공백 제거

## Installation
