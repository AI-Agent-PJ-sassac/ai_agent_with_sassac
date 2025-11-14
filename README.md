# 🏛️ 공공기관 인수인계 AI Agent

공무원 및 공기업 직원들의 업무 인수인계를 돕는 LangGraph 기반 멀티 에이전트 RAG 시스템

## 📌 프로젝트 개요

### 핵심 문제
- 직무 이동 시 인수인계가 제대로 이루어지지 않아 업무 공백 발생
- 과거 작성한 문서나 템플릿을 찾기 어려움
- 작성 방법을 몰라 시간이 오래 걸림

### 솔루션
**"내가 원하는 질문"을 하면 과거 템플릿과 예시를 찾아 정확하고 빠르게 답변**

### 주요 기능
- 📄 **문서 검색**: 과거 작성된 템플릿과 문서를 빠르게 검색
- 💡 **예시 제공**: 실제 작성 사례와 함께 구체적인 가이드 제공
- 🎯 **맥락 이해**: 단순 키워드 검색이 아닌 의도 기반 답변
- ⚡ **빠른 응답**: 질문에 대한 즉각적인 답변과 참고 자료 제공
- 💾 **자동 저장**: 모든 답변 자동 저장 (TXT, JSON, MD)

---

## 🚀 빠른 시작

### 1. 환경 설정

#### 방법 A: uv 사용 (⚡ 추천 - 10배 빠름)

```bash
# 저장소 클론
git clone https://github.com/AI-Agent-PJ-sassac/ai_agent_with_sassac.git

# uv 설치
pip install uv

# 의존성 설치 (자동으로 가상환경 생성)
uv sync

# 가상환경 활성화
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

#### 방법 B: pip 사용 (전통적인 방법)

```bash
# 저장소 클론
git clone https://github.com/yourusername/public-handover-ai.git
cd public-handover-ai

# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 API 키 입력
# UPSTAGE_API_KEY=your_actual_api_key_here
```

### 3. 벡터 DB 생성 (최초 1회)

```bash
# data/ 폴더에 문서 추가
# - PDF, DOCX 파일을 data/ 폴더에 넣으세요
# - 템플릿, 예시, 가이드 문서 등

# 벡터 DB 생성
python vector_store.py
```

### 4. AI Agent 실행 🎉

```bash
python chat.py
```

---

## 💬 사용 방법

### 기본 사용

```bash
python chat.py
```

### 실행 화면

```
============================================================
🏛️  공공기관 인수인계 AI Agent
============================================================
질문을 입력하면 AI가 답변해드립니다.
종료하려면 'quit', 'exit', 'q' 를 입력하세요.
============================================================

🔄 AI Agent 초기화 중...
✅ 벡터 DB 로드 완료
✅ 준비 완료!

❓ 질문: 출장신청서 어떻게 작성하나요?

🤔 답변 생성 중...

============================================================
💬 답변
============================================================
📌 요약:
출장신청서는 출장 목적, 일정, 예상 경비를 작성하여 제출하는 양식입니다.

📝 상세 설명:
1. 출장 목적과 장소 명확히 기재
2. 출장 기간 작성
3. 예상 경비 항목별 작성
4. 상급자 결재 후 제출

💡 작성 팁:
- 출장 3일 전까지 제출 필수
- 예산 범위 내에서 신청
============================================================

❓ 질문: (계속 질문 가능)
```

### 종료 방법

다음 중 하나를 입력:
- `quit`
- `exit`
- `q`
- `종료`
- `Ctrl + C`

---

## 📝 질문 예시

### 🔥 긴급 - 템플릿 찾기
```
예산 신청서 급해요
출장신청서 양식 어디 있어요?
보고서 템플릿 빨리 필요해요
```

### 📄 문서 작성 방법
```
출장신청서 어떻게 작성하나요?
예산 집행 보고서 작성법 알려주세요
보도자료 작성 시 주의사항은?
민원 응대할 때 어떻게 해야 하나요?
```

### 🔄 프로세스/절차
```
장비 구매 절차가 어떻게 되나요?
예산 신청 순서 알려주세요
출장 갈 때 필요한 절차는?
```

### 👥 담당자 찾기
```
예산 관련 담당자 누구예요?
인사팀 연락처 알려주세요
```

---

## 📁 프로젝트 구조

```
public-handover-ai/
├── agents/                      # AI Agent 모듈
│   ├── __init__.py
│   ├── question_analyzer.py    # 질문 분석 Agent
│   ├── search_agent.py         # 검색 Agent
│   ├── answer_generator.py     # 답변 생성 Agent
│   └── verification_agent.py   # 검증 Agent
│
├── data/                        # 문서 데이터
│   ├── *.pdf                   # PDF 문서
│   └── *.docx                  # Word 문서
│
├── chroma_db/                   # 벡터 데이터베이스
│
├── results/                     # 답변 저장 폴더
│   ├── *.txt
│   ├── *.json
│   └── *.md
│
├── chat.py                      # 🌟 대화형 인터페이스 (메인)
├── workflow.py                  # LangGraph 워크플로우
├── vector_store.py             # 벡터 DB 생성
├── document_loader.py          # 문서 로더
├── save_results.py             # 결과 저장
│
├── requirements.txt            # 패키지 목록 (pip용)
├── pyproject.toml              # 프로젝트 설정 (uv용)
├── .env.example               # 환경변수 템플릿
├── .gitignore
└── README.md
```

---

## 🏗️ 시스템 아키텍처

### LangGraph 멀티 에이전트 워크플로우

```
사용자 질문
    ↓
[QuestionAnalyzer]
├─ 의도 분석 (템플릿 찾기/프로세스/일반)
├─ 문서 유형 파악
└─ 긴급도 판단
    ↓
[SearchAgent]
├─ 벡터 검색 (유사도 기반)
├─ 메타데이터 필터링
└─ 문서 분류 (템플릿/예시/관련)
    ↓
[AnswerGenerator]
├─ 구조화된 답변 생성
│   ├─ 📌 요약
│   ├─ 📝 상세 설명
│   └─ 💡 작성 팁
└─ 맥락 기반 커스터마이징
    ↓
[VerificationAgent]
├─ 문서 최신성 확인
├─ 답변 완성도 체크
└─ 의도 일치 여부 검증
    ↓
최종 답변 + 자동 저장
```

---

## 🛠️ 기술 스택

### Core
- **LangGraph**: 멀티 에이전트 오케스트레이션
- **LangChain**: RAG 파이프라인
- **Upstage Solar**: LLM & Embeddings (한국어 특화)

### Vector Store
- **ChromaDB**: 벡터 데이터베이스

### Document Processing
- **PyPDF2**: PDF 처리
- **python-docx**: Word 문서 처리

### Package Manager
- **uv**: 초고속 Python 패키지 관리자 (10-20배 빠름)
- **pip**: 전통적인 패키지 관리자

### Others
- **Python 3.10+**
- **python-dotenv**: 환경 변수 관리

---

## 📊 답변 저장

모든 답변은 자동으로 `results/` 폴더에 3가지 형식으로 저장됩니다:

```
results/
├── rag_result_20241114_153045.txt      # 텍스트
├── rag_result_20241114_153045.json     # JSON
└── rag_result_20241114_153045.md       # Markdown
```

---

## 🔧 고급 사용

### 개별 Agent 테스트

```bash
# 질문 분석 Agent
python agents/question_analyzer.py

# 검색 Agent
python agents/search_agent.py

# 답변 생성 Agent
python agents/answer_generator.py

# 검증 Agent
python agents/verification_agent.py
```

### 전체 워크플로우 테스트

```bash
python workflow.py
```

### 벡터 DB 재생성

```bash
# 기존 DB 삭제 (Windows)
rmdir /s chroma_db

# 기존 DB 삭제 (macOS/Linux)
rm -rf chroma_db/

# 새로 생성
python vector_store.py
```

### 패키지 추가 설치

```bash
# uv 사용 시
uv add 패키지명

# pip 사용 시
pip install 패키지명
```

---

## 🐛 트러블슈팅

### 1. 벡터 DB를 찾을 수 없습니다
```bash
# 해결: 벡터 DB 생성
python vector_store.py
```

### 2. ModuleNotFoundError: No module named 'agents'
```bash
# 해결: 프로젝트 루트에서 실행
cd public-handover-ai
python chat.py
```

### 3. API 키 오류
```bash
# 해결: .env 파일 확인
# UPSTAGE_API_KEY가 제대로 설정되어 있는지 확인
```

### 4. 답변에 참고 문서가 없습니다
```bash
# 해결: data/ 폴더에 문서 추가 후 벡터 DB 재생성
python vector_store.py
```

### 5. NumPy 버전 오류
```bash
# 해결: NumPy 다운그레이드
uv pip install "numpy<2.0"
# 또는
pip install "numpy<2.0"
```

### 6. tokenizers 빌드 오류
```bash
# 해결: transformers 업그레이드 또는 주석 처리
# requirements.txt에서 transformers 라인을 주석 처리하거나
uv pip install "transformers>=4.46.0"
```

---

## 📈 개발 로드맵

### ✅ Phase 1: 기본 RAG (완료)
- [x] 문서 로더 구현
- [x] 벡터 스토어 구축
- [x] 기본 QA 체인

### ✅ Phase 2: LangGraph 멀티 Agent (완료)
- [x] 질문 분석 Agent
- [x] 검색 Agent
- [x] 답변 생성 Agent
- [x] 검증 Agent
- [x] 워크플로우 통합
- [x] 대화형 인터페이스

### 🚧 Phase 3: 고도화 (예정)
- [ ] 하이브리드 검색 (벡터 + 키워드)
- [ ] 메타데이터 자동 추출
- [ ] 예시 매칭 로직 개선
- [ ] 사용자 피드백 수집

### 📋 Phase 4: UI/UX (예정)
- [ ] Streamlit 웹 UI
- [ ] 대화 히스토리
- [ ] 문서 업로드 기능
- [ ] 즐겨찾기 기능

---

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이선스

MIT License

---

## 📧 문의

프로젝트 관련 문의: [your-email@example.com]

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**

---

## 🙏 감사의 말

이 프로젝트는 공공기관의 업무 효율성 향상을 위해 개발되었습니다.