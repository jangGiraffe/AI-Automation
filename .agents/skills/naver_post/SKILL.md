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

### 2. Prepare HTML & Local Images (Step 1-4)
- You can use existing logic to fetch news and generate `blog_post.html`. The generation prompt should ensure images use relative local paths `<img src="image1.png">` and the actual image files exist in the same folder.
- **IMPORTANT Formatting Rules for Generation**:
  - The script parses elements like `p`, `h2`, `h3`, `blockquote`, and `img`.
  - To make the text less plain, strongly use `<blockquote>` around intro texts or key paragraphs.
  - Wrap important phrases or keywords in `<b>` tags (e.g., `<b>중요한 문구</b>`). The python script automatically paints `<b>` tags with a bright blue color when pasting them into Naver!
  - Avoid too many `<br>` tags. The script automatically adds paragraph spacing.
- *Note:* The Selenium script extracts HTML chunks and pastes them block-by-block using Windows clipboard, guaranteeing formatting retention.

### 3. Generate Hashtags (Step 5)
- Optionally generate `hashtags.txt` (comma-separated).

### 4. Upload to Naver (Selenium) (Step 6)
- **Command**: `py .agents/skills/naver_post/scripts/upload_to_naver_selenium.py result/<YYYY-MM-DD> <BlogAlias>`
- This script uses Selenium to:
  1. Auto-login using `pyperclip` bypass.
  2. Enter the SmartEditor ONE environment.
  3. Extract title from `<h1>` and text/images from `<body>`.
  4. Use ActionChains and hidden file inputs or clipboard to structure the post block-by-block.
  5. Publish the post as Private (비공개).
