# 한국어 문장 다듬기

## 프로젝트 개요
한국어 텍스트의 교정, 교열, 윤문을 제공하는 웹 애플리케이션입니다.

## 디렉토리 구조
```
korean-text-corrector/
├── CLAUDE.md           # 프로젝트 문서
├── frontend/           # Next.js 프론트엔드
│   ├── app/           # Next.js 13+ App Router
│   │   ├── layout.tsx # 루트 레이아웃
│   │   ├── page.tsx   # 메인 페이지
│   │   └── globals.css # 전역 스타일
│   ├── components/    # React 컴포넌트
│   │   └── TextCorrector.tsx # 교정 도구 메인 컴포넌트
│   ├── package.json   # 프론트엔드 의존성
│   ├── tsconfig.json  # TypeScript 설정
│   ├── tailwind.config.js # Tailwind CSS 설정
│   └── postcss.config.js  # PostCSS 설정
└── backend/           # 백엔드 서버 (추후 구현)
    └── (API 서버 예정)
```

## 주요 기능
1. **교정 (Proofreading)**: 맞춤법, 띄어쓰기, 문장부호 검사
2. **교열 (Copy Editing)**: 문맥 일관성, 용어 통일, 중복 표현 검토
3. **윤문 (Rewriting)**: 문장 구조 개선, 가독성 향상

## 기술 스택
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS v4
- **Backend**: FastAPI + Python
  - 네이버 맞춤법 검사 API (교정)
  - OpenRouter API (Claude Sonnet 4.5) (교열, 윤문)

## 개발 및 실행
```bash
# 프론트엔드 실행
cd frontend
npm install
npm run dev

# 백엔드 실행
cd backend
pip install -r requirements.txt
python main.py
```

## 구현 상태
- ✅ 프론트엔드 UI 구현 (v0.dev 스타일)
- ✅ 백엔드 API 서버 구현 (FastAPI)
- ✅ 네이버 맞춤법 검사 API 연동 (동적 passportKey 추출)
- ✅ OpenRouter API 연동 (Claude Sonnet 4.5)
- ✅ 순차 처리 로직 (교정 → 교열 → 윤문)
- ✅ 1000자 입력 제한

## 주요 기능 상세
### 교정 (Proofreading)
- 네이버 맞춤법 검사 API 사용
- 맞춤법, 띄어쓰기, 문장부호 자동 교정
- 실패 시 OpenRouter로 자동 폴백

### 교열 (Copy Editing)
- 교정 후 OpenRouter API로 교열 수행
- 문맥 일관성, 용어 통일, 중복 표현 검토

### 윤문 (Rewriting)
- 교정 → 교열 후 윤문 수행
- 문장 구조 개선, 가독성 향상