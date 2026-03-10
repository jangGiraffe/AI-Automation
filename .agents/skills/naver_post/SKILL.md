---
name: create-naver-post
description: Workflow for creating a Naver blog post automatically using Selenium.
---

# Create Naver Post Skill

## Goal
Create a Naver blog post automatically based on an HTML file generated from news or other topics, typing it directly and uploading images via Selenium to bypass Naver SmartEditor ONE's lack of HTML mode.

## Inputs
- **Topic** (주제): The topic to generate the post about.
- **BlogAlias** (블로그 별칭): A short identifier mapping to `.env` variables (e.g., `NAVERMAIN`).

## Environment Setup
1. **Python Dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv selenium webdriver-manager beautifulsoup4 requests pyperclip
   ```
2. **`.env` File**:
   ```env
   # Naver Blog 1
   NAVER_ALIAS_1=NAVERMAIN
   NAVER_ID_1=your_naver_id
   NAVER_PW_1=your_naver_pw
   NAVER_BLOG_NAME_1=your_naver_blog_name
   NAVER_DEFAULT_TOPIC_1=일상,기술
   NAVER_CATEGORIES_1=일상,기술,리뷰
   NAVER_PERSONA_1=친근하고 전문적인 블로거
   ```

## Steps

### 1. Create Output Directory (Step 0)
- Create a folder named `result/<YYYY-MM-DD>_naver` or similar.

### 2. Fetch News (Step 1)
- Use `.agents/skills/naver_post/scripts/fetch_news.py --alias <BlogAlias>` to get recent news items related to the blog's default topics.
  - *Note: This script is shared between Tistory and Naver skills.*
- Source: Google News RSS.
- Output: `.tmp/news_data.json`.

### 3. Prepare HTML & Local Images (Step 2-5)
- **Topic Selection**: Analyze `.tmp/news_data.json` to pick a high-impact news story for the post.
- You can use existing logic to generate `blog_post.html`. The generation prompt should ensure images use relative local paths `<img src="image1.png">` and the actual image files exist in the same folder.
- **IMPORTANT Formatting Rules for Generation**:
  - **Length**: Aim for a **long-form post** (at least 2,500 characters or 7-8 detailed paragraphs). Provide in-depth explanations, practical tips, and expert-like insights to provide high value to readers.
  - **Images**: Always use **at least 2 to 3 images** to make the post visually rich and engaging. Use relative paths like `<img src="image1.png">`, `<img src="image2.png">`, `<img src="image3.png">`.
  - **Structure**: Use multiple `<h2>` and `<h3>` headers to organize the content clearly.
  - **Rich Formatting**: 
    - Strongly use `<blockquote>` around motivational quotes, key takeaways, or introductory/concluding summaries.
    - Wrap important phrases or keywords in `<b>` tags (e.g., `<b>중요한 문구</b>`). These will be automatically highlighted in blue by the upload script.
  - **Paragraphs**: Avoid too many `<br>` tags. The script handles spacing between blocks automatically.
  - **Hashtags**: Include 5-10 relevant hashtags at the bottom of the body text (e.g., `#주제 #키워드`). Naver's editor will recognize these automatically.
- *Note:* The Selenium script extracts HTML chunks and pastes them block-by-block using the Windows clipboard, which perfectly preserves all styles, including the blue bolding.

### 4. Upload to Naver (Selenium) (Step 6)
- **Command**: `py .agents/skills/naver_post/scripts/upload_to_naver_selenium.py result/<YYYY-MM-DD> <BlogAlias>`
- This script uses Selenium to:
  1. Auto-login using `pyperclip` bypass.
  2. Enter the SmartEditor ONE environment.
  3. Extract title from `<h1>` and text/images from `<body>`.
  4. Use ActionChains and hidden file inputs or clipboard to structure the post block-by-block.
  5. Publish the post as Private (비공개).
