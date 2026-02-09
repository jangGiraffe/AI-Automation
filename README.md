# AI Agent & Workflow Automation Repository

**AI 에이전트 및 LLM(Large Language Model)**을 활용한 다양한 업무 자동화 프로젝트를 모아둔 레포지토리입니다.
복잡한 워크플로우를 분석, 설계, 실행하는 AI 기반 자동화 사례들을 연구하고 구현합니다.

---

## 📂 Projects

### 1. AutoPostFlow
**"블로그 포스팅 자동화 워크플로우"**

경제 및 부동산 뉴스(기본값) 또는 **사용자가 요청한 키워드**를 기반으로 뉴스를 수집하고, 분석하여 트렌디한 주제를 선정, AI SEO가 적용된 블로그 포스팅과 이미지/해시태그까지 자동으로 생성하여 구글 드라이브에 업로드하는 프로젝트입니다.

#### 🏗 구조 (3-Layer Architecture)
이 프로젝트는 **지시(Directives) - 조정(Orchestration) - 실행(Execution)**의 3계층 아키텍처를 따릅니다.
- `directives/`: 표준 운영 절차 (SOP) 및 워크플로우 정의
- `execution/`: 실제 작업을 수행하는 Python 스크립트 및 도구
- **Agent**: 지시사항을 해석하고 실행 도구를 적절히 호출하여 목표를 달성하는 AI 역량

#### 🚀 주요 기능
- **뉴스 수집**: Google News RSS 기반 실시간 데이터 수집 (`execution/fetch_news.py`)
- **콘텐츠 생성**: 트렌드 분석 기반 주제 선정 및 HTML 포스팅 작성
- **멀티미디어**: 실사 및 픽셀 아트 스타일 이미지 자동 생성
- **클라우드 연동**: 결과물을 Google Drive로 자동 백업(`execution/upload_to_gdrive.py`) 및 **Tistory 자동 포스팅**(`execution/upload_to_tistory_selenium.py`)

#### 📝 실행 방법
이 프로젝트는 **`directives/blog_post_workflow.md`** 에 정의된 절차를 따릅니다.

1. **설정 (Setup)**:
   - **환경 변수**:
     - `.env.example`을 `.env`로 복사합니다.
     - `GOOGLE_API_KEY`에 **Google AI Studio API Key**를 입력합니다. (이미지 및 해시태그 생성용)
     - **Tistory 설정**: `TISTORY_ID`, `TISTORY_PW`, `TISTORY_BLOG_NAME`을 입력합니다. (자동 업로드용)
   - **Google Drive 인증**:
     - Google Cloud Console에서 다운로드한 `credentials.json` 파일을 프로젝트 루트(`c:\study\autoPostFlow\`)에 위치시킵니다.
     - 최초 실행 시 브라우저 창이 열리며 인증이 진행됩니다.
   - **브라우저**:
     - Selenium 구동을 위해 **Chrome 브라우저**가 설치되어 있어야 합니다.
2. **AI에게 요청**:
   > "`directives/blog_post_workflow.md`에 따라 블로그 포스팅을 진행해줘."

3. **결과물**:
   - `result/[날짜]/` 폴더에 HTML, 이미지, 해시태그 저장
   - 연동된 Google Drive 자동 업로드 및 **Tistory 블로그 비공개 포스팅 완료**

---

## 🛠 Tech Stack
- **Language**: Python 3.14+, Markdown
- **AI/LLM**: Google Gemini (via Agent)
- **Libs**: `urllib`, `google-api-python-client`, `google-auth`

---
*더 많은 AI 자동화 프로젝트가 추가될 예정입니다.*
