# Blog Post Workflow Directive

## Goal
Create a high-impact blog post based on recent economic or real estate news (last 24h), optimized for AI SEO, with specific image and hashtag requirements.

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
    - **Tone**: Informative, easy to understand.
    - **Requirements**:
        - **Style**: Strictly follow the CSS and HTML structure defined in `directives/blog_post_template.html`.
        - **Length**: Minimum 2000 characters. Deep dive analysis required.
        - **Tone**: Professional, authoritative yet accessible (like an expert columnist).
        - **Prohibited**: 
            - Do NOT use phrases like "AI SEO optimized", "I hope this helps", "In this blog post", or any meta-commentary about the writing process.
            - **No Title Prefixes**: Do NOT use prefixes like `[긴급 분석]`, `[속보]`, `[Review]` in the H1 title. Keep the title clean and descriptive.
        - Explain difficult terms simply.
        - Provide concrete examples and data points.
        - Structure: Title (H1), Introduction (Hook), Detailed Analysis (H2s), Practical Implications (H3s), **FAQ (3-5 Q&A)**, Conclusion (Future Outlook).
        - **Footer**: MUST include the following disclaimer at the very bottom:
          > "포함된 이미지는 AI 기술을 활용하여 생성되었습니다."

5.  **Generate Images**:
    -   **Step 5-A: Agent Generation (Preferred)**
        1.  **Check Artifacts First (CRITICAL - DO NOT SKIP)**:
            -   **STRICT RULE**: **Artifacts 패널에 어떤 파일이라도 존재한다면, 무조건 이미지로 간주합니다. 이 경우 `generate_image` 도구 호출은 엄격히 금지됩니다.**
            -   **Action**: 이미지 생성을 시도하기 전, Artifacts 패널을 확인하세요. 파일명이 이미지처럼 보이지 않아도(확장자가 없거나 임의의 이름이라도) **무조건 이미지로 취급**합니다.
            -   **Logic**:
                -   **Duplicate Generation Forbidden**: Artifact가 하나라도 존재하면, 즉시 해당 파일을 `result/<YYYY-MM-DD>/` 폴더로 복사(`copy`) 및 리네임(`image1.png` 등)하고 **이 단계를 즉시 종료**하세요.
                -   **절대로** 이미 있는 Artifact를 무시하고 새로 만들지 마십시오. 이는 불필요한 비용과 시간을 낭비합니다.

        2.  **Generate Images**:
            -   **Condition**: 위 1번 단계에서 **이미지를 하나도 찾지 못했을 경우에만** `generate_image`를 실행합니다.
            -   **Image 1 (Main)**: Realistic, high-quality photo style.
            -   **Image 2 (Context)**: Pixel art (Dot style), fantasy concept.

        3.  **Error Handling & Ghost Success Recovery**:
            -   **Context**: 503 Error나 타임아웃이 발생하더라도 시스템 내부적으로는 이미지가 생성되어 저장되었을 가능성이 매우 높습니다 (스크린샷 증상).
            -   **Action**: 에러 발생 시 즉시 재시도하지 말고, 5초 대기 후 `find_by_name`으로 다시 `*.png`를 검색하세요.
            -   **Recovery**: 새로 생성된 파일이 발견되면 에러 메시지를 무시하고 1번 단계의 복사/리네임 로직을 수행하세요.

    - **Step 5-B: Script Fallback (Automation/Retry)**
        - If the Agent fails or if running in a fully automated mode without an active agent session:
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
