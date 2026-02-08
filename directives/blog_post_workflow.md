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

1.  **Fetch News**:
    - Use `execution/fetch_news.py` to get recent news items.
    - Source: Google News RSS.
    - Output: `.tmp/news_data.json` containing titles, links, pubDates, and descriptions.

2.  **Select Topic**:
    - Analyze the news items.
    - Criteria: High impact, potential for high click-through rate (CTR), relevant to general public.

3.  **Generate Content**:
    - **Format**: HTML (ready to paste into a blog editor).
    - **Tone**: Informative, easy to understand.
    - **Requirements**:
        - **Style**: Strictly follow the CSS and HTML structure defined in `directives/blog_post_template.html`.
        - **Length**: Minimum 2000 characters. Deep dive analysis required.
        - **Tone**: Professional, authoritative yet accessible (like an expert columnist).
        - **Prohibited**: Do NOT use phrases like "AI SEO optimized", "I hope this helps", "In this blog post", or any meta-commentary about the writing process.
        - Explain difficult terms simply.
        - Provide concrete examples and data points.
        - Structure: Title (H1), Introduction (Hook), Detailed Analysis (H2s), Practical Implications (H3s), **FAQ (3-5 Q&A)**, Conclusion (Future Outlook).
        - **Footer**: MUST include the following disclaimer at the very bottom:
          > "포함된 이미지는 AI 기술을 활용하여 생성되었습니다."

4.  **Generate Images**:
    - **Image 1 (Main)**: Realistic, high-quality photo style relevant to the news topic. Builds trust.
    - **Image 2 (Context)**: Pixel art (Dot style), World of Warcraft fantasy concept, metaphorically related to the topic.
    - **Output**: Images should be saved in the **same directory** as the HTML file (Flat Structure).

    > **Note**: If image generation fails (e.g., 429 Quota Exceeded or 400 Billing Required), proceed to Step 4-1.

4-1. **Retry Image Generation (Optional)**:
    - If images are missing due to API limits, use the retry script.
    - Command: `py execution/retry_images.py <path_to_html_file>`
    - **Logic**: 
        - Parses HTML for `<img>` tags.
        - Prioritizes `data-prompt` (or `alt`).
        - Retries with Gemini (Imagen) API until successful.
        - Updates HTML `src` if necessary (removes `images/` prefix for flat structure).

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

## Output
- `blog_post.html`: The complete blog post content.

- `hashtags.txt`: List of hashtags.
- **Directory naming convention**:
    - Default: `result/<YYYY-MM-DD>/`
    - If exists: `result/<YYYY-MM-DD>(1)/`, `result/<YYYY-MM-DD>(2)/`, etc.
