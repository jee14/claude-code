# 한국어 교정 도구 프로젝트

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
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Backend**: (추후 구현 예정 - Python/FastAPI 또는 Node.js)

## 개발 및 실행
```bash
# 프론트엔드 실행
cd frontend
npm install
npm run dev
```

## 구현 상태
- ✅ 프론트엔드 UI 구현
- ✅ 목업 교정 로직 구현
- ⏳ 백엔드 API 서버 구현 예정
- ⏳ 실제 한국어 처리 엔진 연동 예정

## 향후 계획
1. 백엔드 API 서버 구축
2. 한국어 NLP 라이브러리 연동 (KoNLPy, Kiwipiepy 등)
3. 네이버/카카오 맞춤법 검사 API 연동
4. 사용자 인증 및 히스토리 기능
5. 배치 처리 기능