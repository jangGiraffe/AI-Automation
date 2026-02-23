---
name: create-tistory-post
description: Workflow for creating a high-impact Tistory blog post based on recent news, optimized for AI SEO, with specific image and hashtag requirements.
---

# Create Tistory Post Skill

## Goal
Create an **ultra-long-form, high-impact 'Mega Content'** Tistory blog post (30,000~40,000 characters) based on recent economic, IT, or real estate news, optimized for AI SEO with deep structural analysis and visualization.

## Inputs
- **Topic** (주제): The topic to generate the post about (e.g. "미국 주식", "비트코인", "금리 인상"). If not provided, the Agent should use the default topic for the alias (`TISTORY_DEFAULT_TOPIC_<ALIAS>`).
- **BlogAlias** (블로그 별칭): A short identifier for the target blog (e.g. `MONEY`, `TECH`, `PERSONAL`).
- Region: South Korea (KR)
- Language: Korean (ko)
  - *Tip: If you want to fetch foreign news, specify the Host Language (`--hl`) and Geolocation (`--gl`) flags in the fetch step (e.g. `--hl en --gl US` for US English).*
- **Google Drive**:
    - Folder ID: Managed in `.env` as `GOOGLE_DRIVE_PARENT_FOLDER_ID`.
    - Credentials Path: `credentials.json` (User must provide)

## Environment Setup
Before using this skill, ensure the following dependencies and environment variables are configured.

1. **Python Dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv selenium webdriver-manager beautifulsoup4 requests feedparser
   ```
2. **`.env` File** (must be located in the directory where you run the scripts, typically project root):
   You can register up to 5 Tistory blogs using `_1`, `_2`, etc., and specify their custom alias (`TISTORY_ALIAS_1`).
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_DRIVE_PARENT_FOLDER_ID=your_gdrive_folder_id

   # Blog 1
   TISTORY_ALIAS_1=MONEY
   TISTORY_ID_1=your_money_email
   TISTORY_PW_1=your_money_password
   TISTORY_BLOG_NAME_1=your_money_blog_name
   TISTORY_DEFAULT_TOPIC_1=경제,주식,부동산

   # Blog 2
   TISTORY_ALIAS_2=TECH
   TISTORY_ID_2=your_tech_email
   TISTORY_PW_2=your_tech_password
   TISTORY_BLOG_NAME_2=your_tech_blog_name
   TISTORY_DEFAULT_TOPIC_2=IT,인공지능,스타트업
   TISTORY_PERSONA_2=IT 트렌드에 민감한 로봇 (예시)
   
   # ... Add up to 5 blogs following this pattern (_1 to _5).
   ```
3. **Google Drive Credentials**:
   - Place a `credentials.json` file in the root directory for Google Drive API access.

## Steps

### 1. Create Output Directory (Step 0)
- **Action**: Create a folder named `result/<YYYY-MM-DD>`.
- **Duplicate Rule**: If the folder already exists, append `_1`, `_2`, etc. to the folder name.
- **Rule**: All subsequent files (`blog_post.html`, images, `hashtags.txt`) MUST be saved directly inside this folder.
- *Example*: `result/2026-02-09/blog_post.html`

### 2. Fetch News
- Use `.agents/skills/tistory_post/scripts/fetch_news.py --alias <BlogAlias> "<Topic>"` to get recent news items related to the requested topic.
  - *If `<Topic>` is omitted or empty, the script will automatically use the `TISTORY_DEFAULT_TOPIC_<ALIAS>` from `.env`.*
  - *By default, the script fetches half Korean (`--hl ko --gl KR`) and half US English (`--hl en --gl US`) news for the given topic.*
  - *Optional: To override this and fetch strictly from one region, append `--hl <lang> --gl <region>` (e.g., `--hl ja --gl JP` for strictly Japanese news).*
- Source: Google News RSS.
- Output: `.tmp/news_data.json` containing titles, links, pubDates, and descriptions.

### 3. Select Topic & Category (Step 2)
- Analyze the news items.
- Criteria for Topic: High impact, potential for high click-through rate (CTR), relevant to general public.
- **Category Selection**: 
  - Look up `TISTORY_CATEGORIES_X` corresponding to the chosen `<BlogAlias>` in the `.env` file.
  - Pick the ONE most relevant category from that comma-separated list.
  - Output this exact category string into `result/<YYYY-MM-DD>/category.txt`.

### 4. Fetch Internal Links (Step 3)
- Use `.agents/skills/tistory_post/scripts/fetch_rss_links.py <BlogName>` to get recent post titles and links from the blog's RSS.
  - *Note: `<BlogName>` is the technical Tistory blog name (e.g. `iammoneyoil`), NOT the alias.*
- Output: `.tmp/internal_links.json`.
- Purpose: To provide data for internal linking in the new post.

### 5. Generate Content (Step 4)
- **Format**: HTML (ready to paste into a blog editor).
- **Persona & Tone**: 
    - **Stricly Follow**: Look up `TISTORY_PERSONA_X` corresponding to the chosen `<BlogAlias>` in the `.env` file.
    - **Style**: Embody this persona completely throughout the post. If no persona is defined, default to a professional yet friendly tone.
    - **Tone**: The tone (degree of formality, vocabulary, etc.) should match the persona. Default is "친근한 ~요체" but can be overridden by the persona description.
- **Requirements (Mega Content Standard)**:
    - **Style**: Strictly follow the CSS and HTML structure defined in `.agents/skills/tistory_post/templates/blog_post_template.html`.
    - **Image Rule**: `<figure>` 태그의 `data-ke-mobilestyle`은 반드시 `"widthContent"`를 사용.
    - **Length**: **초장문 메가 콘텐츠 (30,000~40,000자 내외)**. 단순히 양을 늘리는 것이 아니라, 독자가 전자책 한 권을 읽는 듯한 깊이를 제공해야 합니다.
    - **Structural Depth**:
        - **Detailed 목차 (Table of Contents)**: 포스팅 시작 부분에 클릭 가능한 구조의 상세 목차를 포함하세요.
        - **Multi-level Headings**: 최소 8개 이상의 `<h2>` 주제를 설정하고, 각 주제 하위에 `<h3>`, `<h4>` 소주제를 촘촘하게 배치하여 논리적 구조를 완성하세요.
    - **Insightful Analysis**: 
        - 단순 뉴스 요약 금지. 
        - **입체적 분석**: 기술적 원리, 역사적 배경, 글로벌 시장(US, China 등)과의 비교, 관련 주식/경제 지표 영향 분석 등을 포함하세요.
        - **시각화**: 필요시 HTML `<table>`을 사용하여 데이터를 비교하거나 정돈된 정보를 제공하세요.
    - **Persona Alignment**:
        - 단순 정보 전달을 넘어, 설정된 **페르소나의 관점**에서 분석과 의견을 제시하세요.
        - 말투, 어조, 문장 구조 등이 페르소나의 성격(예: 냉철한 분석가, 다정한 이웃, 미래형 로봇 등)을 충실히 반영해야 합니다.
    - **Tone**: 페르소나 설정에 따르되, 기본적으로 독자와 소통하는 느낌을 유지하세요.
    - **Prohibited**: 
        - **NO Markdown Syntax**: Do NOT use Markdown formatting (e.g., `**bold**`, `# Heading`, `- list`, `[link](url)`). Everything MUST be written in pure HTML (e.g., `<b>bold</b>`, `<h2>Heading</h2>`, `<ul><li>list</li></ul>`, `<a href="...">link</a>`).
        - Do NOT use phrases like "AI SEO optimized", "I hope this helps", "In this blog post", or any meta-commentary about the writing process.
        - **No Title Prefixes**: Do NOT use prefixes like `[긴급 분석]`, `[속보]`, `[Review]` in the H1 title.
    - **Readability Rules**:
        - Break long paragraphs into smaller 2-3 sentence chunks.
        - Insert an empty `<p data-ke-size="size16">&nbsp;</p>` between text paragraphs.
        - Ensure a horizontal divider `<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style1" />` is placed right above every `<h2>` heading.
    - **Content Modules**: 
        - Title (H1)
        - **Introduction**: 
            - **Persona-based Hook**: Greetings and introductions MUST align with the `TISTORY_PERSONA_X`.
            - Do NOT simply say "안녕하세요. 지랩봇입니다." unless the persona is "지랩봇".
            - Introduce yourself or set the stage in a way that fits the writer's concept.
        - Detailed TOC
        - Comprehensive Analysis Sections (8+ main sections)
        - Case Studies or Global Comparisons
        - **FAQ (10+ detailed Q&A for SEO)**
        - Conclusion (Future Outlook & Final Thoughts).
    - **Internal Links**: Max 3 related posts from `.tmp/internal_links.json`.
    - **Footer**: MUST include the following disclaimers:
      > "Powered by jangGiraffe GitHub" (with a hyperlink to https://github.com/jangGiraffe/AI-Automation)
      > "포함된 이미지는 AI 기술을 활용하여 생성되었습니다."

### 6. Generate Images (Step 5)
- **⚠️ CRITICAL: 대화 중단/재개 시 규칙 (MUST READ FIRST)**:
    - `generate_image` 호출은 **canceled, failed, timeout 등 어떤 상태로 표시되더라도, 시스템 내부에서 이미지가 이미 생성되었을 가능성이 매우 높습니다.**
    - **따라서**: `generate_image`를 호출한 적이 있는 대화에서 "Continue" 등으로 재개될 경우, **다른 어떤 작업보다 먼저 Brain 폴더 수색(Step 5-A-3)을 즉시 실행**하세요.
    - **절대 금지**: 이전에 `generate_image`를 호출한 적 있는데 Brain 검색 없이 이미지를 다시 생성하는 행위.
    - **판단 기준**: `generate_image` 호출 결과가 canceled/failed/error로 보이면 → **100% Brain 검색부터 실행**. 사용자에게 물어보지 말고 자동으로 수행하세요.

#### Step 5-A: Agent Generation (Preferred)
1. **Check Artifacts First (CRITICAL - DO NOT SKIP)**:
    - **STRICT RULE**: **Artifacts 패널에 어떤 파일이라도 존재한다면, 무조건 이미지로 간주합니다. 이 경우 `generate_image` 도구 호출은 엄격히 금지됩니다.**
    - **Action**: 이미지 생성을 시도하기 전, Artifacts 패널을 확인하세요. 파일명이 이미지처럼 보이지 않아도(확장자가 없거나 임의의 이름이라도) **무조건 이미지로 취급**합니다.
    - **Logic**:
        - **Duplicate Generation Forbidden**: Artifact가 하나라도 존재하면, 즉시 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 복사(`copy`) 및 리네임(`image1.png` 등)하고 **이 단계를 즉시 종료**하세요.
        - **절대로** 이미 있는 Artifact를 무시하고 새로 만들지 마십시오. 이는 불필요한 비용과 시간을 낭비합니다.

2. **Generate Images**:
    - **Pre-check (Brain Search)**: `generate_image` 호출 전, **Brain 폴더**(`C:\Users\<USER>\.gemini\antigravity\brain`)를 먼저 수색하여 최근 생성된 이미지가 있는지 확인하세요.
    - **Condition**: Artifacts 및 Brain 폴더에서 **이미지를 하나도 찾지 못했을 경우에만** `generate_image`를 실행합니다.
    - **Image 1 (Main)**: Realistic, high-quality photo style.
    - **Image 2 (Context)**: Pixel art (Dot style), fantasy concept.

3. **Verify Generation (Mandatory Brain Search — 자동 실행 필수)**:
    - **Context**: `generate_image` 호출 후, 툴의 성공/전송 취소/에러 여부와 관계없이 시스템이 내부적으로 이미지를 생성했을 가능성이 높습니다.
    - **TRIGGER**: 이 단계는 `generate_image` 호출 결과를 받은 **즉시, 자동으로, 사용자 지시 없이** 실행해야 합니다. 사용자에게 "확인해볼까요?" 같은 질문 금지.
    - **Action**: 이미지 생성 시도 후에는 **반드시 사용자의 `.gemini` Brain 폴더를 수색**하세요.
        - **Path**: `C:\Users\<USER>\.gemini\antigravity\brain` (윈도우 기준, `<USER>`는 현재 사용자명)
        - **Method**: `Get-ChildItem -Recurse` 명령어를 사용하여 최근 10분 내 생성된 `.png` 파일을 찾으세요.
        - **Specifics**: `image1`, `image2` 또는 Artifact Name 패턴(`semiconductor_economy` 등)이 포함된 파일을 찾습니다.
    - **Recovery**: 
        - **발견 시**: 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 즉시 복사(`Copy-Item`)하고, 파일명을 규칙에 맞게 변경(`image1.png` 등)한 후 단계를 종료(성공 처리)하세요.
        - **미발견 시**: Artifacts 패널 확인을 사용자에게 요청하거나, 최후의 수단으로 폴백 스크립트를 실행하세요.

#### Step 5-B: Script Fallback (Automation/Retry)
- If the Agent fails or if running in a fully automated mode without an active agent session:
- **MUST: Brain Search First (Step 5-A-3 실행)**:
    - 스크립트를 실행하기 **전에**, 반드시 **Step 5-A-3 (Verify Generation)** 의 Brain 폴더 수색을 먼저 수행하세요.
    - `.gemini/antigravity/brain` 폴더에서 최근 생성된 이미지가 있는지 확인합니다.
    - **이미지가 발견되면** 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 복사하고, 스크립트 실행 없이 이 단계를 종료합니다.
    - **이미지가 없을 경우에만** 아래 스크립트를 실행합니다.
- Use `.agents/skills/tistory_post/scripts/retry_images.py`.
- Command: `py .agents/skills/tistory_post/scripts/retry_images.py <path_to_html_file>`
- This script uses the `GOOGLE_API_KEY` from `.env`.

### 7. Generate Hashtags (Step 6)
- 10 relevant hashtags for blog visibility.
- **Retry Logic**: If hashtags are missing or fail to generate initially, use `.agents/skills/tistory_post/scripts/generate_hashtags.py`.
- Command: `py .agents/skills/tistory_post/scripts/generate_hashtags.py <path_to_html_file>`
- Logic: Reads HTML text content, requests hashtags from Gemini API (REST), and appends them to the HTML.

### 8. Upload to Google Drive (Step 7)
- Command: `py .agents/skills/tistory_post/scripts/upload_to_gdrive.py result/<YYYY-MM-DD>`
- **Logic**:
    - Reads parent folder ID from `.env`.
    - Checks for existing folder at `result/<YYYY-MM-DD>` (or creates indexed version if exists).
    - Uploads all content to the date-indexed folder on Google Drive.
- Requires `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `python-dotenv`.

### 9. Upload to Tistory (Selenium) (Step 8)
- **Goal**: Automate posting to Tistory blog using Selenium WebDriver for a specific `BlogAlias`.
- **Command**: `py .agents/skills/tistory_post/scripts/upload_to_tistory_selenium.py result/<YYYY-MM-DD> <BlogAlias>` (Be sure to convert the alias to UPPERCASE).
- **Prerequisites**:
    - `.env` must contain `TISTORY_ALIAS_X`, `TISTORY_ID_X`, `TISTORY_PW_X`, `TISTORY_BLOG_NAME_X` matching the alias.
    - Chrome browser installed.
- **Process**:
    - Auto-login to Kakao/Tistory.
    - Injects HTML content.
    - **Image Upload**: Replaces local image placeholders (`src="image1.png"`) with actual uploaded images by switching to Basic Mode.
    - **Hashtags**: Injects tags from `hashtags.txt` (or extracted from HTML).
    - **Publish**: Saves as **Private** (비공개) for final review.
- **Note**: Monitor the browser for any 2FA or CAPTCHA requirements during login.

## Output
- `blog_post.html`: The complete blog post content.
- `hashtags.txt`: List of hashtags.
- `category.txt`: The selected blog category from .env.
- **Directory naming convention**:
    - Default: `result/<YYYY-MM-DD>/`
    - If exists: `result/<YYYY-MM-DD>_1/`, `result/<YYYY-MM-DD>_2/`, etc.
