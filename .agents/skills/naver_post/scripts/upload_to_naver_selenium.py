import os
import sys
import time
import pyperclip
import pyautogui
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

load_dotenv()

def set_clipboard_html(html_str, plain_str):
    """Copies HTML and Plain text directly to Windows Clipboard to retain formatting."""
    import ctypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    CF_HTML = user32.RegisterClipboardFormatW("HTML Format")
    
    fragment = html_str.encode('utf-8')
    header_template = (
        "Version:0.9\r\n"
        "StartHTML:{0:08d}\r\n"
        "EndHTML:{1:08d}\r\n"
        "StartFragment:{2:08d}\r\n"
        "EndFragment:{3:08d}\r\n"
    )
    prefix = b"<html>\r\n<body>\r\n<!--StartFragment-->\r\n"
    suffix = b"\r\n<!--EndFragment-->\r\n</body>\r\n</html>"
    
    header_len = 93
    start_frag = header_len + len(prefix)
    end_frag = start_frag + len(fragment)
    end_html = end_frag + len(suffix)
    header = header_template.format(header_len, end_html, start_frag, end_frag).encode('utf-8')
    
    cf_html_data = header + prefix + fragment + suffix
    cf_text_data = plain_str.encode('utf-16le') + b'\x00\x00'
    
    user32.OpenClipboard(0)
    user32.EmptyClipboard()
    
    h_mem_html = kernel32.GlobalAlloc(0x0042, len(cf_html_data) + 1)
    p_mem_html = kernel32.GlobalLock(h_mem_html)
    ctypes.memmove(p_mem_html, cf_html_data, len(cf_html_data))
    kernel32.GlobalUnlock(h_mem_html)
    user32.SetClipboardData(CF_HTML, h_mem_html)
    
    h_mem_text = kernel32.GlobalAlloc(0x0042, len(cf_text_data))
    p_mem_text = kernel32.GlobalLock(h_mem_text)
    ctypes.memmove(p_mem_text, cf_text_data, len(cf_text_data))
    kernel32.GlobalUnlock(h_mem_text)
    user32.SetClipboardData(CF_UNICODETEXT, h_mem_text)
    
    user32.CloseClipboard()

def safe_send_keys_clipboard(driver, element, text):
    """Fallback method using clipboard paste to bypass strict formatting or captcha."""
    element.click()
    time.sleep(0.2)
    pyperclip.copy(text)
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
    time.sleep(0.5)

def main():
    if len(sys.argv) < 3:
        print("Usage: py upload_to_naver_selenium.py <result_folder_path> <BlogAlias>")
        sys.exit(1)

    result_folder = sys.argv[1]
    blog_alias = sys.argv[2].upper()
    html_file = os.path.join(result_folder, "blog_post.html")
    hashtag_file = os.path.join(result_folder, "hashtags.txt")

    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
        sys.exit(1)

    # 1. Fetch credentials
    naver_id = None
    naver_pw = None
    blog_name = None

    for i in range(1, 6):
        env_alias = os.getenv(f"NAVER_ALIAS_{i}")
        if env_alias and env_alias.upper() == blog_alias:
            naver_id = os.getenv(f"NAVER_ID_{i}")
            naver_pw = os.getenv(f"NAVER_PW_{i}")
            blog_name = os.getenv(f"NAVER_BLOG_NAME_{i}")
            break

    if not naver_id or not naver_pw:
        print(f"Error: Could not find credentials for alias '{blog_alias}' in .env")
        sys.exit(1)

    if not blog_name:
        blog_name = naver_id # Default to ID if not specified

    # 2. Parse HTML and Hashtags
    print(f"Reading and parsing content from {html_file}...")
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Extract title
    title = "AI Generated Blog Post"
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text().strip()
        h1.decompose()

    # 1. Force black color on all general text blocks to prevent style bleeding
    for tag in soup.find_all(['p', 'li', 'h2', 'h3', 'h4', 'blockquote']):
        existing_style = tag.get('style', '')
        # Only add black if color not already set (unlikely here but safe)
        if 'color' not in existing_style.lower():
            tag['style'] = f"color: #000000; {existing_style}".strip()

    # 2. Apply blue color to important phrases (bold text)
    for bold in soup.find_all(['b', 'strong']):
        existing_style = bold.get('style', '')
        bold['style'] = f"color: #0054FF; font-weight: bold; {existing_style}".strip()

    # Extract body blocks (html chunks, img formatting)
    blocks = []
    current_html_chunk = []
    
    # Process children of body if exists, else descendants
    root = soup.body if soup.body else soup
    
    for element in root.children:
        if element.name == 'img':
            if current_html_chunk:
                blocks.append(('html', "".join(current_html_chunk)))
                current_html_chunk = []
            
            src = element.get('src')
            if src and not src.startswith('http') and not src.startswith('//'):
                blocks.append(('img', src))
        elif element.name is not None:
            # any other block (h2, p, blockquote)
            current_html_chunk.append(str(element))

    if current_html_chunk:
        blocks.append(('html', "".join(current_html_chunk)))

    # Read hashtags
    hashtags = ""
    if os.path.exists(hashtag_file):
        with open(hashtag_file, "r", encoding="utf-8") as f:
            hashtags = f.read().strip().replace("#", "").replace(" ", ", ")

    # 3. Setup Selenium
    print("Starting Chrome Driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 4. Login to Naver
        login_url = "https://nid.naver.com/nidlogin.login"
        print(f"Navigating to {login_url}...")
        driver.get(login_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "id"))
            )
            
            # Use clipboard paste to bypass captcha
            print("Logging in via clipboard paste bypass...")
            id_input = driver.find_element(By.ID, "id")
            safe_send_keys_clipboard(driver, id_input, naver_id)

            pw_input = driver.find_element(By.ID, "pw")
            safe_send_keys_clipboard(driver, pw_input, naver_pw)

            driver.find_element(By.ID, "log.login").click()
        except TimeoutException:
            print("Login form not found. Maybe already logged in?")

        # Wait for login success
        print("Waiting for login to complete (Handle 2FA manually if prompted)...")
        WebDriverWait(driver, 60).until(
            EC.url_changes(login_url)
        )
        time.sleep(3) # Let sessions set

        # 5. Go to Write Page
        write_url = f"https://blog.naver.com/{blog_name}?Redirect=Write"
        print(f"Navigating to write page: {write_url}...")
        driver.get(write_url)

        # 5. Handle initial popups / Help panels
        print("Handling initial popups...")
        # Try both in default and iframe areas
        def close_popups():
            # Close 'Help', 'Tutorial', and 'Restore Draft' (작성 중인 글...) panels
            help_close_selectors = [
                "button.se-popup-button-cancel",     # 'Cancel' (취소) for draft restoration
                "button.se-help-panel-close-button",
                "button[aria-label='도움말 닫기']",
                ".se-popup-button-cancel",
                ".se-popup-button-close",
                "button.se-popup-close-button",
                "button.se-help-panel-button",
                "label.se-help-panel-checkbox-label" # 'Don't see again'
            ]
            for sel in help_close_selectors:
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, sel)
                    for btn in btns:
                        if btn.is_displayed():
                            # If it's a restore draft popup, we want to check for specific text if possible
                            # but clicking 'cancel' is generally safe for these types of overlays at start
                            btn.click()
                            print(f"Handled popup/help/draft-cancel using: {sel}")
                            time.sleep(1)
                except: continue

            # Extra check for the specific 'Restore Draft' text if needed
            try:
                # XPATH for the 'Cancel' button specifically in the restore draft container
                restore_cancel = driver.find_element(By.XPATH, "//div[contains(@class, 'se-popup-container')]//button[contains(@class, 'se-popup-button-cancel')]")
                if restore_cancel.is_displayed():
                    restore_cancel.click()
                    print("Specifically dismissed 'Restore Draft' popup via XPATH.")
                    time.sleep(1)
            except: pass

        # 1st try in default context (sometimes overlays are here)
        close_popups()

        # Switch to mainFrame iframe
        try:
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame")))
            print("Switched to mainFrame iframe.")
        except TimeoutException:
            print("mainFrame not found. Assuming SmartEditor ONE is on main DOM.")

        # 2nd try inside iframe (Editor popups are usually here)
        close_popups()

        # 6. Title Input
        print("Setting title...")
        try:
            # Re-find the title element using safe logic and click it
            title_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".se-documentTitle"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_container)
            time.sleep(1)
            
            # Click exactly on the placeholder span to ensure focus
            try:
                placeholder = title_container.find_element(By.CSS_SELECTOR, "span.se-placeholder")
                placeholder.click()
            except:
                title_container.click()
            time.sleep(1)

            # Type title
            pyperclip.copy(title)
            webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
            time.sleep(1)

            # Explicitly move to body by clicking the main container or hitting ENTER
            print("Moving focus to body...")
            try:
                # Try clicking the first paragraph placeholder or the main container
                body_placeholder = driver.find_element(By.CSS_SELECTOR, ".se-component-content span.se-placeholder")
                body_placeholder.click()
            except:
                try:
                    main_container = driver.find_element(By.CSS_SELECTOR, ".se-main-container")
                    main_container.click()
                except:
                    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)
        except Exception as e:
            print(f"Warning: Title input failed: {e}")

        # 7. Body Input Block by Block
        print("Typing body content and uploading images...")
        time.sleep(1)
        
        actions = webdriver.ActionChains(driver)

        for block_type, content in blocks:
            if block_type == 'html':
                try:
                    plain_text = BeautifulSoup(content, 'html.parser').get_text()
                    set_clipboard_html(content, plain_text)
                except Exception as e:
                    print("Clipboard HTML set failed, fallback to plain.", e)
                    pyperclip.copy(BeautifulSoup(content, 'html.parser').get_text())
                
                actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                time.sleep(1)
                
                # Force reset style after EACH pasted chunk by typing a space at the end
                # and then applying a "black" formatting block.
                print("Resetting style chain to black...")
                try:
                    # Clear formatting by pasting a DIV with explicit black color.
                    # This is more robust than a span in some editor versions.
                    set_clipboard_html('<div style="color:#000000; font-family:inherit;">&nbsp;</div>', " ")
                    webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    time.sleep(0.5)
                except:
                    pass

                # Adds extra empty lines for paragraph spacing
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(0.3)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(1)

            elif block_type == 'img':
                abs_path = os.path.abspath(os.path.join(result_folder, content))
                if os.path.exists(abs_path):
                    print(f"Attempting image upload for: {abs_path}")
                    uploaded = False
                    
                    # METHOD 1: Direct Hidden Input Injection (Most reliable if element is found)
                    try:
                        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        for fi in file_inputs:
                            accept = fi.get_attribute("accept")
                            if accept and "image" in accept:
                                # Make it visible just in case for older engines
                                driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", fi)
                                fi.send_keys(abs_path)
                                print("Method 1 (Hidden Input) successful.")
                                uploaded = True
                                break
                    except Exception as e:
                        print(f"Method 1 failed: {e}")

                    # METHOD 2: UI Click + PyAutoGUI (Fallback)
                    if not uploaded:
                        try:
                            photo_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-name='image'], button.se-image-toolbar-button, .se-toolbar-item-image button"))
                            )
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", photo_btn)
                            time.sleep(1)
                            photo_btn.click()
                            print("Method 2: Clicked Photo button. Waiting 3s for dialog...")
                            time.sleep(3)

                            # Robust PyAutoGUI sequence
                            # 1. Clear field (Alt+N focuses filename in Windows)
                            pyautogui.hotkey('alt', 'n')
                            time.sleep(0.5)
                            pyautogui.press('backspace', presses=10) # Clear
                            
                            # 2. Paste path
                            pyperclip.copy(abs_path)
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(1)
                            
                            # 3. Enter
                            pyautogui.press('enter')
                            print("Method 2: Path sent via pyautogui.")
                            uploaded = True
                        except Exception as e:
                            print(f"Method 2 failed: {e}")

                    if uploaded:
                        time.sleep(10) # Wait for upload processing
                        # Click back to editor body to regain focus
                        try:
                            driver.find_element(By.CSS_SELECTOR, ".se-main-container").click()
                        except: pass
                        
                        actions = webdriver.ActionChains(driver)
                        actions.send_keys(Keys.ENTER).perform()
                        actions.send_keys(Keys.ENTER).perform()
                        time.sleep(1)
                else:
                    print(f"Warning: Local image not found at {abs_path}")

        # 8. PUBLISH PHASE
        print("Starting Publish Phase...")
        try:
            # 8.1 Open Publish Menu
            # First, ensure we are in default content to find the main publish button
            driver.switch_to.default_content()
            
            publish_selectors = [
                "button.publish_btn__m9KHH[data-click-area='tpb.publish']",
                "button[data-click-area='tpb.publish']",
                "button.publish_btn__m9KHH",
                "button.button_publish", 
                ".se-publish-button button"
            ]
            
            publish_config_btn = None
            for sel in publish_selectors:
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, sel)
                    for b in btns:
                        if b.is_displayed():
                            publish_config_btn = b; break
                    if publish_config_btn: break
                except: continue
            
            if not publish_config_btn:
                # Try inside iframe as fallback
                try:
                    driver.switch_to.frame("mainFrame")
                    btns = driver.find_elements(By.XPATH, "//button[contains(., '발행')]")
                    for b in btns:
                        if b.is_displayed():
                            publish_config_btn = b; break
                except: pass
            
            if not publish_config_btn:
                driver.switch_to.default_content()
                publish_config_btn = driver.find_element(By.XPATH, "//button[contains(., '발행')]")

            print("Clicking initial Publish button to open menu...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", publish_config_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", publish_config_btn)
            
            # 8.2 Wait for and Handle the Publish Layer
            print("Waiting for publish configuration layer/popup...")
            try:
                # Wait for the specific layer provided by user or any common layer
                publish_layer = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-focus-lock='publishLayer'], .publish_layer, .se-publish-config-layer"))
                )
                print("Publish layer detected.")
                time.sleep(2)
            except:
                print("Warning: Publish layer not detected via CSS, Proceeding with broad search.")

            # 8.3 Add Hashtags (Inside the layer)
            if hashtags:
                print("Adding hashtags in publish menu...")
                try:
                    # Look for the specific tag input provided by user
                    tag_input = None
                    tag_selectors = [
                        "input#tag-input.tag_input__rvUB5", 
                        "input#tag-input", 
                        "input.tag_input__rvUB5",
                        "input[placeholder*='태그']", 
                        ".se-tag-input"
                    ]
                    for sel in tag_selectors:
                        try:
                            found = driver.find_elements(By.CSS_SELECTOR, sel)
                            for f in found:
                                if f.is_displayed():
                                    tag_input = f; break
                            if tag_input: break
                        except: continue
                    
                    if tag_input:
                        tag_input.click()
                        time.sleep(0.5)
                        for tag in hashtags.split(','):
                            tag = tag.strip()
                            if tag:
                                pyperclip.copy(tag)
                                # Type the tag and press ENTER
                                webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                                time.sleep(0.5)
                                pyautogui.press('enter')
                                time.sleep(0.3)
                    else:
                        print("Warning: Could not find hashtag input in the publish menu layer.")
                except Exception as e:
                    print(f"Warning: Hashtag input failed: {e}")

            # 8.4 Select 'Private' (비공개)
            try:
                # Usually there's a label or span with '비공개'
                # We search for visible labels within the layer
                private_btns = driver.find_elements(By.XPATH, "//label[contains(., '비공개')] | //span[contains(., '비공개')]")
                for pb in private_btns:
                    if pb.is_displayed():
                        pb.click()
                        print("Selected 'Private' (비공개).")
                        time.sleep(1)
                        break
            except Exception as e:
                print(f"Warning: Private selection failed: {e}")

            # 8.5 FINAL SUBMIT
            print("Clicking Final Publish Submit button...")
            final_publish_btn = None
            confirm_selectors = [
                "button.confirm_btn__WEaBq[data-testid='seOnePublishBtn']",
                "button.confirm_btn__WEaBq",
                "button[data-testid='seOnePublishBtn']",
                "button[data-click-area='tpb*i.publish']",
                "button.publish_btn__m9KHH",
                "button.button_confirm",
                ".se-btn-publish"
            ]
            
            # We must find the button that is VISIBLE (the bottom one in the popup)
            for sel in confirm_selectors:
                try:
                    potential_btns = driver.find_elements(By.CSS_SELECTOR, sel)
                    for pb in potential_btns:
                        # Check visibility and make sure it's the one with text or specific role
                        if pb.is_displayed():
                            # Usually the final button is the last one in the DOM or has text '발행'
                            btn_text = pb.text.strip()
                            if "발행" in btn_text or "확인" in btn_text or not btn_text:
                                final_publish_btn = pb
                                break
                    if final_publish_btn: break
                except: continue

            if not final_publish_btn:
                # Last resort: XPATH based search for visible button with '발행'
                try:
                    potential_btns = driver.find_elements(By.XPATH, "//button[contains(., '발행')] | //button[contains(., '확인')]")
                    for pb in potential_btns:
                        if pb.is_displayed():
                            final_publish_btn = pb; break
                except: pass

            if final_publish_btn:
                # Use JS click as it bypasses "element not interactable" or "intercepted" 
                # which often happens in complex overlays
                driver.execute_script("arguments[0].click();", final_publish_btn)
                print(">> POST PUBLISHED SUCCESSFULLY (Private)!")
                time.sleep(10)
            else:
                print("Error: Could not find the final publish button in the layer.")

        except Exception as e:
             print(f"Failed to publish: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script execution finished. Browser will close in 5 seconds.")
        time.sleep(5)
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
