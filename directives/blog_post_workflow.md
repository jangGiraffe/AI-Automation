# Blog Post Workflow Directive

## Goal
Create a high-impact blog post based on recent economic or real estate news (last 6h), optimized for AI SEO, with specific image and hashtag requirements.

## Inputs
- Keywords: "경제" (Economy), "부동산" (Real Estate)
- Region: South Korea (KR)
- Language: Korean (ko)
- **Google Drive**:
    - Folder ID: Managed in `.env` as `GOOGLE_DRIVE_PARENT_FOLDER_ID`.
    - Credentials Path: `credentials.json` (User must provide)

## Steps

1.  **Create Output Directory** (Step 0):
    -   **Action**: Create a folder named `result/<YYYY-MM-DD>`.
    -   **Duplicate Rule**: If the folder already exists, append `_1`, `_2`, etc. to the folder name.
    -   **Rule**: All subsequent files (`blog_post.html`, images, `hashtags.txt`) MUST be saved directly inside this folder.
    -   *Example*: `result/2026-02-09/blog_post.html`

2.  **Fetch News**:
    - Use `execution/fetch_news.py` to get recent news items.
    - Source: Google News RSS.
    - Output: `.tmp/news_data.json` containing titles, links, pubDates, and descriptions.

3.  **Select Topic**:
    - Analyze the news items.
    - Criteria: High impact, potential for high click-through rate (CTR), relevant to general public.

4.  **Generate Content**:
    - **Format**: HTML (ready to paste into a blog editor).
    - **Tone**: Informative, easy to understand, friendly (친근한 ~요체).
    - **Requirements**:
        - **Style**: Strictly follow the CSS and HTML structure defined in `directives/blog_post_template.html`.
        - **Image Rule**: `<figure>` 태그의 `data-ke-mobilestyle`은 반드시 `"widthContent"`를 사용. (`widthOrigin` 사용 금지 — 넓은 화면에서 이미지가 본문 영역을 넘어 튀어나옴)
        - **Length**: 약 4000자 (3800~4200자). Deep dive analysis required.
        - **Tone**: 친근하고 편안한 말투 (~요체). 전문적이지만 딱딱하지 않게, 옆에서 설명해주는 느낌. 예: "~인데요", "~거든요", "~해볼게요", "~같아요".
        - **Prohibited**: 
            - Do NOT use phrases like "AI SEO optimized", "I hope this helps", "In this blog post", or any meta-commentary about the writing process.
            - **No Title Prefixes**: Do NOT use prefixes like `[긴급 분석]`, `[속보]`, `[Review]` in the H1 title. Keep the title clean and descriptive.
        - Explain difficult terms simply.
        - Provide concrete examples and data points.
        - Structure: Title (H1), Introduction (Hook), Detailed Analysis (H2s), Practical Implications (H3s), **FAQ (3-5 Q&A)**, Conclusion (Future Outlook).
        - **Footer**: MUST include the following disclaimer at the very bottom:
          > "포함된 이미지는 AI 기술을 활용하여 생성되었습니다."

5.  **Generate Images**:
    -   **⚠️ CRITICAL: 대화 중단/재개 시 규칙 (MUST READ FIRST)**:
        -   `generate_image` 호출은 **canceled, failed, timeout 등 어떤 상태로 표시되더라도, 시스템 내부에서 이미지가 이미 생성되었을 가능성이 매우 높습니다.**
        -   **따라서**: `generate_image`를 호출한 적이 있는 대화에서 "Continue" 등으로 재개될 경우, **다른 어떤 작업보다 먼저 Brain 폴더 수색(Step 5-A-3)을 즉시 실행**하세요.
        -   **절대 금지**: 이전에 `generate_image`를 호출한 적 있는데 Brain 검색 없이 이미지를 다시 생성하는 행위.
        -   **판단 기준**: `generate_image` 호출 결과가 canceled/failed/error로 보이면 → **100% Brain 검색부터 실행**. 사용자에게 물어보지 말고 자동으로 수행하세요.

    -   **Step 5-A: Agent Generation (Preferred)**
        1.  **Check Artifacts First (CRITICAL - DO NOT SKIP)**:
            -   **STRICT RULE**: **Artifacts 패널에 어떤 파일이라도 존재한다면, 무조건 이미지로 간주합니다. 이 경우 `generate_image` 도구 호출은 엄격히 금지됩니다.**
            -   **Action**: 이미지 생성을 시도하기 전, Artifacts 패널을 확인하세요. 파일명이 이미지처럼 보이지 않아도(확장자가 없거나 임의의 이름이라도) **무조건 이미지로 취급**합니다.
            -   **Logic**:
                -   **Duplicate Generation Forbidden**: Artifact가 하나라도 존재하면, 즉시 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 복사(`copy`) 및 리네임(`image1.png` 등)하고 **이 단계를 즉시 종료**하세요.
                -   **절대로** 이미 있는 Artifact를 무시하고 새로 만들지 마십시오. 이는 불필요한 비용과 시간을 낭비합니다.

        2.  **Generate Images**:
            -   **Pre-check (Brain Search)**: `generate_image` 호출 전, **Brain 폴더**(`C:\Users\<USER>\.gemini\antigravity\brain`)를 먼저 수색하여 최근 생성된 이미지가 있는지 확인하세요.
            -   **Condition**: Artifacts 및 Brain 폴더에서 **이미지를 하나도 찾지 못했을 경우에만** `generate_image`를 실행합니다.
            -   **Image 1 (Main)**: Realistic, high-quality photo style.
            -   **Image 2 (Context)**: Pixel art (Dot style), fantasy concept.

        3.  **Verify Generation (Mandatory Brain Search — 자동 실행 필수)**:
            -   **Context**: `generate_image` 호출 후, 툴의 성공/전송 취소/에러 여부와 관계없이 시스템이 내부적으로 이미지를 생성했을 가능성이 높습니다.
            -   **TRIGGER**: 이 단계는 `generate_image` 호출 결과를 받은 **즉시, 자동으로, 사용자 지시 없이** 실행해야 합니다. 사용자에게 "확인해볼까요?" 같은 질문 금지.
            -   **Action**: 이미지 생성 시도 후에는 **반드시 사용자의 `.gemini` Brain 폴더를 수색**하세요.
                -   **Path**: `C:\Users\<USER>\.gemini\antigravity\brain` (윈도우 기준, `<USER>`는 현재 사용자명)
                -   **Method**: `Get-ChildItem -Recurse` 명령어를 사용하여 최근 10분 내 생성된 `.png` 파일을 찾으세요.
                -   **Specifics**: `image1`, `image2` 또는 Artifact Name 패턴(`semiconductor_economy` 등)이 포함된 파일을 찾습니다.
            -   **Recovery**: 
                -   **발견 시**: 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 즉시 복사(`Copy-Item`)하고, 파일명을 규칙에 맞게 변경(`image1.png` 등)한 후 단계를 종료(성공 처리)하세요.
                -   **미발견 시**: Artifacts 패널 확인을 사용자에게 요청하거나, 최후의 수단으로 폴백 스크립트를 실행하세요.

    - **Step 5-B: Script Fallback (Automation/Retry)**
        - If the Agent fails or if running in a fully automated mode without an active agent session:
        - **MUST: Brain Search First (Step 5-A-3 실행)**:
            - 스크립트를 실행하기 **전에**, 반드시 **Step 5-A-3 (Verify Generation)** 의 Brain 폴더 수색을 먼저 수행하세요.
            - `.gemini/antigravity/brain` 폴더에서 최근 생성된 이미지가 있는지 확인합니다.
            - **이미지가 발견되면** 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 복사하고, 스크립트 실행 없이 이 단계를 종료합니다.
            - **이미지가 없을 경우에만** 아래 스크립트를 실행합니다.
        - Use `execution/retry_images.py`.
        - Command: `py execution/retry_images.py <path_to_html_file>`
        - This script uses the `GOOGLE_API_KEY` from `.env`.

6.  **Generate Hashtags**:
    - 10 relevant hashtags for blog visibility.
    - **Retry Logic**: If hashtags are missing or fail to generate initially, use `execution/generate_hashtags.py`.
    - Command: `py execution/generate_hashtags.py <path_to_html_file>`
    - Logic: Reads HTML text content, requests hashtags from Gemini API (REST), and appends them to the HTML.

7.  **Upload to Google Drive**:
    - Command: `py execution/upload_to_gdrive.py result/<YYYY-MM-DD>`
    - **Logic**:
        - Reads parent folder ID from `.env`.
        - Checks for existing folder at `result/<YYYY-MM-DD>` (or creates indexed version if exists).
        - Uploads all content to the date-indexed folder on Google Drive.
    - Requires `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `python-dotenv`.

8.  **Upload to Tistory (Selenium)**:
    - **Goal**: Automate posting to Tistory blog using Selenium WebDriver.
    - **Command**: `py execution/upload_to_tistory_selenium.py result/<YYYY-MM-DD>`
    - **Prerequisites**:
        - `.env` must contain `TISTORY_ID`, `TISTORY_PW`, `TISTORY_BLOG_NAME`.
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
- **Directory naming convention**:
    - Default: `result/<YYYY-MM-DD>/`
    - If exists: `result/<YYYY-MM-DD>(1)/`, `result/<YYYY-MM-DD>(2)/`, etc.
