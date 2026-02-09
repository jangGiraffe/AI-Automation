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

4.  **Generate Images**:
    - **Step 4-A: Agent Generation (Preferred)**
        - The AI Agent attempts to generate images using the `generate_image` tool during the interactive session.
        - **Image 1 (Main)**: Realistic, high-quality photo style.
        - **Image 2 (Context)**: Pixel art (Dot style), fantasy concept.
        - *Note*: This saves the user's API quota if the Agent's tool is available.

    - **Step 4-B: Script Fallback (Automation/Retry)**
        - If the Agent fails or if running in a fully automated mode without an active agent session:
        - Use `execution/retry_images.py`.
        - Command: `py execution/retry_images.py <path_to_html_file>`
        - This script uses the `GOOGLE_API_KEY` from `.env`.

5.  **Generate Hashtags**:
    - 10 relevant hashtags for blog visibility.
    - **Retry Logic**: If hashtags are missing or fail to generate initially, use `execution/generate_hashtags.py`.
    - Command: `py execution/generate_hashtags.py <path_to_html_file>`
    - Logic: Reads HTML text content, requests hashtags from Gemini API (REST), and appends them to the HTML.

6.  **Upload to Google Drive**:
    - Command: `py execution/upload_to_gdrive.py result/<YYYY-MM-DD>`
    - **Logic**:
        - Reads parent folder ID from `.env`.
        - Checks for existing folder at `result/<YYYY-MM-DD>` (or creates indexed version if exists).
        - Uploads all content to the date-indexed folder on Google Drive.
    - Requires `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `python-dotenv`.

7.  **Upload to Tistory (Selenium)**:
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
