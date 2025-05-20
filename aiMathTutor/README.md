# AI 수학 튜터

RAG와 OpenAI를 활용한 적응형 수학 문제 생성 시스템

## 환경 설정

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
- `.env.example` 파일을 `.env`로 복사
- OpenAI API 키 설정:
  ```bash
  cp .env.example .env
  ```
- `.env` 파일에서 `your_openai_api_key_here`를 실제 API 키로 교체

## 실행 방법

```bash
streamlit run app.py
```

## 주요 기능

- OpenAI 기반 문제 생성
- RAG 기반 유사 문제 검색 및 변형
- 객관식 문제 자동 생성
- 적응형 난이도 조절
- 연관 개념 추천

## 보안 주의사항

- `.env` 파일은 절대로 Git에 커밋하지 마세요
- API 키는 안전하게 관리해주세요 