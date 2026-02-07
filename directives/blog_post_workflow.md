# Blog Post Workflow Directive

## Goal
Create a high-impact blog post based on recent economic or real estate news (last 24h), optimized for AI SEO, with specific image and hashtag requirements.

## Inputs
- Keywords: "경제" (Economy), "부동산" (Real Estate)
- Region: South Korea (KR)
- Language: Korean (ko)
- **Google Drive**:
    - Folder ID: `YOUR_FOLDER_ID` (Set in .env or provide at runtime)
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

5.  **Generate Hashtags**:
    - 10 relevant hashtags for blog visibility.

6.  **Upload to Google Drive**:
    - Upload the entire `result/<YYYY-MM-DD>` folder to the specified Google Drive Folder ID.
    - Requires `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

## Output
- `blog_post.html`: The complete blog post content.
- `images/`: Directory containing the generated images.
- `hashtags.txt`: List of hashtags.
- **Directory naming convention**:
    - Default: `result/<YYYY-MM-DD>/`
    - If exists: `result/<YYYY-MM-DD>(1)/`, `result/<YYYY-MM-DD>(2)/`, etc.
