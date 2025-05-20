# AI 수학 튜터 - RAG 기반 문제 생성 시스템

## 프로젝트 소개
이 프로젝트는 RAG(Retrieval-Augmented Generation) 기술을 활용하여 맞춤형 수학 문제를 생성하고 관리하는 시스템입니다.

## 주요 기능
- OpenAI API를 활용한 수학 문제 생성
- 문제 저장 및 관리
- 사용자 풀이 기록 관리
- 사용자별 통계 분석
- 힌트 생성 및 답안 검증

## 설치 방법
1. 프로젝트 클론
```bash
git clone https://github.com/yourusername/AI-StudyAssistant.git
cd AI-StudyAssistant
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
# .env 파일 생성
OPENAI_API_KEY=your_api_key_here
```

## 사용 방법
1. 서버 실행
```bash
python aiMathTutor/app.py
```

2. 웹 브라우저에서 접속
```
http://localhost:8000
```

## 프로젝트 구조
```
aiMathTutor/
├── core/
│   ├── problem/
│   │   ├── repository.py     # 문제 저장소
│   │   ├── generator.py      # 문제 생성
│   │   ├── validator.py      # 유효성 검증
│   │   └── formatter.py      # 포맷 변환
│   └── openai/
│       └── api_client.py     # OpenAI API 클라이언트
├── data/
│   ├── generated_problems.json   # 생성된 문제 저장
│   └── user_history.json        # 사용자 기록 저장
└── app.py                       # 메인 애플리케이션
```

## 기여 방법
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 