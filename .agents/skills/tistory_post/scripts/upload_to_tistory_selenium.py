import os
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import pyperclip

# Load environment variables
load_dotenv()

def main():
    if len(sys.argv) < 3:
        print("Usage: py upload_to_tistory_selenium.py <result_folder_path> <BlogAlias>")
        sys.exit(1)

    result_folder = sys.argv[1]
    blog_alias = sys.argv[2].upper()
    html_file = os.path.join(result_folder, "blog_post.html")
    hashtag_file = os.path.join(result_folder, "hashtags.txt")

    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
        sys.exit(1)

    # 1. Read Content
    print(f"Reading content from {html_file}...")
    with open(html_file, "r", encoding="utf-8") as f:
        content_html = f.read()

    hashtags = ""
    # Try reading from hashtags.txt
    if os.path.exists(hashtag_file):
        with open(hashtag_file, "r", encoding="utf-8") as f:
            hashtags = f.read().strip().replace("#", "").replace(" ", ", ")
    else:
        # Fallback: Extract from HTML
        print("hashtags.txt not found. Extracting from HTML...")
        # Use findall because there might be an empty placeholder div first
        matches = re.findall(r'<div class="hashtag-section"[^>]*>(.*?)</div>', content_html, re.DOTALL)
        tags_list = []
        for raw_text in matches:
            cleaned = re.sub(r'<[^>]+>', '', raw_text).strip()
            if cleaned:
                # Split by space, remove #
                for t in cleaned.split():
                    t_clean = t.replace("#", "").strip()
                    if t_clean:
                        tags_list.append(t_clean)
        
        if tags_list:
             # Remove duplicates while preserving order
             seen = set()
             deduped = []
             for t in tags_list:
                 if t not in seen:
                     deduped.append(t)
                     seen.add(t)
             hashtags = ", ".join(deduped)
             print(f"Extracted tags: {hashtags}")
        else:
             print("No tags found in HTML.")

    # Try reading from category.txt
    category_file = os.path.join(result_folder, "category.txt")
    target_category = ""
    if os.path.exists(category_file):
        with open(category_file, "r", encoding="utf-8") as f:
            target_category = f.read().strip()
        print(f"Target Category: '{target_category}'")

    # 2. Setup Selenium
    tistory_id = None
    tistory_pw = None
    blog_name = None

    for i in range(1, 6):
        env_alias = os.getenv(f"TISTORY_ALIAS_{i}")
        if env_alias and env_alias.upper() == blog_alias:
            tistory_id = os.getenv(f"TISTORY_ID_{i}")
            tistory_pw = os.getenv(f"TISTORY_PW_{i}")
            blog_name = os.getenv(f"TISTORY_BLOG_NAME_{i}")
            break

    if not tistory_id or not tistory_pw or not blog_name:
        print(f"Error: Could not find complete credentials for alias '{blog_alias}' in .env")
        sys.exit(1)

    print("Starting Chrome Driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 3. Login
        login_url = "https://www.tistory.com/auth/login"
        print(f"Navigating to {login_url}...")
        driver.get(login_url)
        
        # Click 'Kakao Login' button
        try:
            kakao_login_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_login.link_kakao_id"))
            )
            kakao_login_btn.click()
        except TimeoutException:
            print("Kakao login button not found or already on login page.")

        # Kakao Login Form
        print("Waiting for Kakao Login page...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "loginId"))
            )
            
            id_input = driver.find_element(By.NAME, "loginId")
            id_input.clear()
            id_input.send_keys(tistory_id)
            id_input.send_keys(Keys.ENTER)
            
            time.sleep(1)

            pw_input = driver.find_element(By.NAME, "password")
            pw_input.clear()
            pw_input.send_keys(tistory_pw)
            pw_input.send_keys(Keys.ENTER)
        except TimeoutException:
             print("Login elements not found. Check if already logged in.")

        # 4. Wait for Login Completion
        print("Waiting for login to complete... (Please handle 2FA/Captcha manually if needed)")
        WebDriverWait(driver, 120).until(
            EC.url_contains("tistory.com")
        )
        print("Login detected (no longer on login page). Waiting 30 seconds for any final redirects or manual steps...")
        time.sleep(30)

        # 5. Go to Write Page
        write_url = f"https://{blog_name}.tistory.com/manage/post"
        print(f"Navigating to write page: {write_url}...")
        driver.get(write_url)
        
        try:
            WebDriverWait(driver, 6).until(EC.alert_is_present())
            driver.switch_to.alert.dismiss()
        except TimeoutException:
            pass

        try:
            # Title input is #post-title-inp (textarea)
            title_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "post-title-inp"))
            )
        except TimeoutException:
            print("Could not find title input field (#post-title-inp). Dumping page source...")
            with open("debug_page_source_2.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        # Helper for non-BMP characters (emojis)
        def safe_send_keys(element, text):
            if not text:
                text = "untitle"
            driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];
                element.value = text;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
            """, element, text)
            # Fallback check
            val = element.get_attribute("value")
            if not val:
                element.send_keys(text)

        # Set Title
        title_match = re.search(r'<h1>(.*?)</h1>', content_html)
        title = title_match.group(1) if title_match else "AI Generated Blog Post"
        title = "".join(c for c in title if ord(c) <= 0xFFFF)
        
        print(f"Setting title: {title}")
        try:
            # Scroll to title and click to focus
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_input)
            time.sleep(0.5)
            title_input.click()
            time.sleep(0.5)
            
            # Use ActionChains to ensure the editor's internal state updates
            # Select all and type/paste
            actions = webdriver.ActionChains(driver)
            actions.click(title_input)
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.BACKSPACE).perform()
            time.sleep(0.5)
            
            # Using safe_send_keys as a backup, but primary is typing or pasting
            pyperclip.copy(title)
            actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
            actions.perform()
            
            # Final check/force
            current_val = title_input.get_attribute("value")
            if not current_val:
                safe_send_keys(title_input, title)
                
            print(f"  Title set to: {title_input.get_attribute('value')[:20]}...")
        except Exception as e:
            print(f"  Warning: Title setting error: {e}")
        time.sleep(2)

        # ----------------------------------------------------------------------
        # INITIAL CONTENT INJECTION (DRAFT)
        # ----------------------------------------------------------------------
        print("Injecting draft HTML content...")
        
        # Robust Switch to HTML Mode
        # Robust Switch to HTML Mode
        def switch_to_html_mode(driver):
            try:
                # Check if already in HTML mode (CodeMirror visible)
                cms = driver.find_elements(By.CSS_SELECTOR, ".CodeMirror")
                if cms and cms[0].is_displayed():
                    print("Already in HTML mode.")
                    return True

                print("Switching to HTML Mode...")
                try:
                    # Method 1: UI Clicks
                    mode_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "editor-mode-layer-btn-open")))
                    mode_btn.click()
                    time.sleep(0.5)
                    
                    try:
                        # Try finding by text "HTML"
                        html_btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'HTML')]")))
                        html_btn.click()
                    except:
                        # Fallback to ID
                        driver.find_element(By.ID, "editor-mode-html").click()
                    
                    try: driver.switch_to.alert.accept()
                    except: pass
                    
                except Exception as ui_e:
                    print(f"UI switch failed ({ui_e}), trying JS...")
                    # Method 2: JS Force
                    driver.execute_script("tistory.editor.ChangeMode.toHtml();")

                # Verify
                time.sleep(2)
                cms = driver.find_elements(By.CSS_SELECTOR, ".CodeMirror")
                if cms and cms[0].is_displayed():
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Error switching to HTML mode: {e}")
                return False

        if not switch_to_html_mode(driver):
            print("Retry switching to HTML mode (JS Force)...")
            driver.execute_script("try { tistory.editor.ChangeMode.toHtml(); } catch(e) { console.log(e); }")
            time.sleep(2)

        time.sleep(1)
        # Paste Draft
        pyperclip.copy(content_html)
        actions = webdriver.ActionChains(driver)
        # Focus Editor reliably
        try:
            print("Focusing editor...")
            driver.find_element(By.CSS_SELECTOR, ".CodeMirror").click()
        except Exception as e:
             print(f"Focus warning: {e}")

        time.sleep(0.5)
        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        time.sleep(3)

        # Helper to switch to Basic Mode
        def switch_to_basic_mode(driver):
            print("Switching to Basic Mode (User-Defined Selectors)...")
            
            try:
                # 1. Open Mode Menu (Look for button with text 'HTML')
                print("  >> Clicking 'HTML' mode button to open menu...")
                # Try specific structure first: button > i.mce-txt "HTML"
                try:
                    mode_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[.//i[contains(@class, 'mce-txt') and text()='HTML']]"))
                    )
                except:
                    # Fallback: just text contains HTML
                    mode_btn = WebDriverWait(driver, 5).until(
                         EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'HTML')]"))
                    )
                
                mode_btn.click()
                time.sleep(0.5)
                
                # 2. Click Basic Mode (ID: editor-mode-kakao-tistory)
                print("  >> Clicking 'Basic Mode' (editor-mode-kakao-tistory)...")
                basic_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "editor-mode-kakao-tistory"))
                )
                basic_btn.click()
                    
                time.sleep(1)
                
                # Handle potential alert (e.g., "Content may be modified...")
                print("  >> Waiting for mode switch alert...")
                try: 
                    # Tistory often shows a native confirm: "Writing mode... changes..."
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    print(f"  >> Alert detected: {alert.text}")
                    alert.accept()
                    print("  >> Alert accepted.")
                except TimeoutException:
                    print("  >> No alert appeared within 5s.")
                except Exception as e:
                    print(f"  >> Verified alert interaction failed: {e}")
                
                return True
                
            except Exception as e:
                print(f"  >> UI Switch failed: {e}")
                # Fallback to JS if UI fails totally
                try:
                    driver.execute_script("tistory.editor.ChangeMode.toWysiwyg();")
                    return True
                except:
                    return False

        # ----------------------------------------------------------------------
        # SWITCH TO BASIC MODE FOR IN-PLACE UPLOAD
        # ----------------------------------------------------------------------
        if not switch_to_basic_mode(driver):
            print("Failed to switch to Basic Mode. Aborting upload loop.")
        
        time.sleep(2)

        # ----------------------------------------------------------------------
        # IMAGE UPLOAD PROCESS (In-Place Replacement)
        print("\nScanning for local images to replace...")
        
        # Regex to capture content of src="..." avoiding http/https
        # We capture anything ending in image extensions, then filter.
        # Modified to be slightly more permissive but still filter out http
        print(f"DEBUG: Content HTML length: {len(content_html)}")
        raw_matches = re.findall(r'src=["\']([^"\']+\.(?:png|jpg|jpeg|gif))["\']', content_html, re.IGNORECASE)
        print(f"DEBUG: Initial raw matches: {raw_matches}")
        
        unique_images = []
        
        for m in raw_matches:
            if m.startswith("http") or m.startswith("//"): 
                continue
            if m not in unique_images:
                unique_images.append(m)
        
        print(f"DEBUG: Unique images to process: {unique_images}")
        
        if unique_images:
            print(f"Found {len(unique_images)} images to replace: {unique_images}")
            
            for local_path in unique_images:
                # Handle relative paths vs absolute paths
                # Ensure result_folder is absolute
                abs_result_folder = os.path.abspath(result_folder)
                
                if os.path.isabs(local_path):
                    abs_path = local_path
                else:
                    abs_path = os.path.join(abs_result_folder, local_path)
                
                print(f"DEBUG: Checking path: {abs_path}")
                
                if not os.path.exists(abs_path):
                    print(f"  Warning: File not found locally: {abs_path}")
                    continue
                    
                filename = os.path.basename(local_path)
                print(f"\nProcessing: {filename}")
                
                try:
                    # 1. Find the placeholder image in the editor (Basic Mode)
                    # Use JS to find img with matching src substring (since formatting might differ)
                    # We escape backslashes for JS string
                    js_path_search = local_path.replace("\\", "\\\\")
                    
                    placeholder = None
                    try:
                        # Try exact match first
                        placeholder = driver.find_element(By.CSS_SELECTOR, f"img[src*='{filename}']")
                    except:
                        # Fallback to any broken image if filename match fails?
                        # Let's try to focus by clicking the 'broken image' icon if evident
                        print("  Could not find specific placeholder img by filename. Checking for any local-path img...")
                        imgs = driver.find_elements(By.TAG_NAME, "img")
                        
                        # Debug: Print all images found
                        print(f"  DEBUG: Found {len(imgs)} images in editor.")
                        for i, img in enumerate(imgs):
                             try:
                                 src = img.get_attribute("src")
                                 print(f"    [Img {i}] src: {src}")
                             except:
                                 print(f"    [Img {i}] src: (error getting src)")

                        for img in imgs:
                            src = img.get_attribute("src")
                            if not src: continue
                            
                            # Check if filename is in src (This handles relative paths resolved to http)
                            if filename in src:
                                print(f"  DEBUG: Found candidate img by filename match: {src}")
                                placeholder = img
                                break
                            
                            # Old fallback: Check if src is a local file path pattern
                            if "file:///" in src or "c:" in src.lower():
                                print(f"  DEBUG: Found candidate img by local path pattern: {src}")
                                placeholder = img
                                break
                    
                    # 1. Find the placeholder image (Check Iframe first)
                    print("  Searching for placeholder image...")
                    placeholder = None
                    
                    # Store main handle
                    main_window = driver.current_window_handle
                    
                    # Try finding in main content
                    try:
                        placeholder = driver.find_element(By.CSS_SELECTOR, f"img[src*='{filename}']")
                        print("    Found in main document.")
                    except:
                        # Try searching IFRAMEs
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        print(f"    Not in main. Checking {len(iframes)} iframes...")
                        for i, iframe in enumerate(iframes):
                            try:
                                driver.switch_to.frame(iframe)
                                try:
                                    placeholder = driver.find_element(By.CSS_SELECTOR, f"img[src*='{filename}']")
                                    print(f"    Found in iframe index {i}.")
                                    
                                    # Focus/Select it using JS (More robust than click)
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", placeholder)
                                    time.sleep(0.5)
                                    
                                    # Create specific selection range on the image
                                    driver.execute_script("""
                                        var img = arguments[0];
                                        var range = document.createRange();
                                        range.selectNode(img);
                                        var sel = window.getSelection();
                                        sel.removeAllRanges();
                                        sel.addRange(range);
                                    """, placeholder)
                                    print("    Forced JS selection on image.")
                                    time.sleep(0.5)
                                    
                                    break # Keep in this frame to delete? No, need to go back for toolbar.
                                    # We will delete it later.
                                except:
                                    driver.switch_to.default_content()
                            except:
                                driver.switch_to.default_content()
                        
                        driver.switch_to.default_content()

                    if not placeholder:
                        print("  Placeholder not found. Uploading at current cursor position.")

                    # 2. Click 'Attach' to trigger DOM (User ID: mceu_0-open)
                    print("  Clicking 'Attach' button (#mceu_0-open)...")
                    try:
                        attach_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "mceu_0-open"))
                        )
                        attach_btn.click()
                        time.sleep(1)
                    except Exception as e:
                        print(f"  Attach button click failed: {e}") 
                        # Continue anyway to try finding input

                    # 3. Click 'Photo' menu item (User ID: attach-image)
                    # User says: "Then click Photo in the floating menu"
                    print("  Clicking 'Photo' menu item (div#attach-image)...")
                    try:
                         # Target the DIV explicitly
                         photo_btn = WebDriverWait(driver, 3).until(
                             EC.element_to_be_clickable((By.CSS_SELECTOR, "div#attach-image"))
                         )
                         photo_btn.click()
                    except Exception as e:
                         print(f"  Photo button click failed: {e}")

                    time.sleep(1)

                    # 4. Direct Input targeting
                    print("  Targeting input#attach-image (Correcting ID conflict)...")
                    try:
                         # STRICTLY target the INPUT, not the DIV
                         file_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input#attach-image"))
                        )
                         
                         # Make it visible so we can interact
                         driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", file_input)
                         
                         # Send keys
                         file_input.send_keys(abs_path)
                         print("  File sent to input#attach-image.")
                         
                    except Exception as e:
                        print(f"  Upload input target failed: {e}")
                        # Fallback: Generic file input
                        try:
                             file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                             file_input.send_keys(abs_path)
                             print("  Fallback input success.")
                        except:
                             continue

                    # 5. Wait for upload to complete

                    # 5. Wait for upload to complete
                    print("  Waiting for upload (6s)...")
                    time.sleep(6)
                    
                    # 6. Remove the placeholder (Old Image)
                    if placeholder:
                        print("  Removing old placeholder...")
                        try:
                            # Must go back to iframe if needed
                            iframes = driver.find_elements(By.TAG_NAME, "iframe")
                            for iframe in iframes:
                                driver.switch_to.frame(iframe)
                                try:
                                    ph = driver.find_element(By.CSS_SELECTOR, f"img[src*='{filename}']")
                                    driver.execute_script("arguments[0].remove();", ph)
                                    print("    Removed in iframe.")
                                    break
                                except:
                                    driver.switch_to.default_content()
                            driver.switch_to.default_content()
                        except:
                            print("  Could not remove placeholder.")
                            driver.switch_to.default_content()
                            
                except Exception as e:
                    print(f"  Error processing image {filename}: {e}")

        else:
            print("No local images found in draft.")

        # ----------------------------------------------------------------------
        # FINALIZATION (No Repaste Needed)
        # ----------------------------------------------------------------------
        print("\nUploads complete. Content should be ready.")
        time.sleep(2)
        
        # Just ensure we are in Basic Mode (redundant check)
        try: driver.switch_to.alert.accept()
        except: pass

        # 7. Tags
        print("Adding tags...")
        try:
            # Wait for tag input
            tag_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "tagText"))
            )
            # Scroll to it
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tag_input)
            time.sleep(0.5)
            
            tag_input.clear()
            safe_send_keys(tag_input, hashtags)
            tag_input.send_keys(Keys.ENTER)
            print("  Tags added.")
        except TimeoutException:
            print("  Tag input (#tagText) not found within timeout.")
        except Exception as e:
             print(f"  Error adding tags: {e}")

        # 8. Publish
        # 8. Publish
        print("Publishing (Private)...")
        try:
            # 1. Set Category (If provided) BEFORE clicking publish layer button
            if target_category:
                print(f"  Setting category to: {target_category}...")
                try:
                    # Depending on editor mode, we might need to scroll or JS click
                    cat_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "category-btn"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cat_btn)
                    time.sleep(0.5)
                    try:
                        cat_btn.click()
                    except:
                        driver.execute_script("arguments[0].click();", cat_btn)
                    time.sleep(0.5)
                    
                    cat_item = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[@id='category-list']//div[contains(@class, 'mce-menu-item') and contains(., '{target_category}')]"))
                    )
                    # Click via JS fallback to avoid interception
                    driver.execute_script("arguments[0].click();", cat_item)
                    print(f"  Category '{target_category}' selected.")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  Warning: Could not select category '{target_category}'. Is it created in Tistory? Error: {e}")

            # 2. Click 'Complete' (완료)
            publish_layer_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish-layer-btn"))
            )
            driver.execute_script("arguments[0].click();", publish_layer_btn)
            time.sleep(1.5)
            
            # 3. Select Private
            print("  Selecting 'Private' visibility...")
            try:
                # Try explicit radio ID first (common ones)
                try: driver.find_element(By.ID, "public-visibility-private").click() 
                except: pass
                
                # Try label text
                chk = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//label[contains(., '비공개')]"))
                )
                chk.click()
            except Exception as e:
                print(f"  Warning: Private selection issue: {e}")

            time.sleep(1)

            # 3. Final Publish (Private Save)
            print("  Verifying title before final publish...")
            try:
                # Re-find title input to be safe
                final_title_check = driver.find_element(By.ID, "post-title-inp")
                t_val = final_title_check.get_attribute("value")
                if not t_val or t_val.strip() == "":
                    print("  Title is missing! Attempting emergency title injection...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_title_check)
                    final_title_check.click()
                    time.sleep(0.5)
                    pyperclip.copy(title if 'title' in locals() else "untitle")
                    webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    time.sleep(1)
                else:
                    print(f"  Title verified: {t_val[:20]}...")
            except:
                pass

            print("  Clicking 'Private Save' (#publish-btn)...")
            final_save_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish-btn"))
            )
            # Use JS click as it is more robust to overlays
            driver.execute_script("arguments[0].click();", final_save_btn)
            
            print(">> POST PUBLISHED (Private)!")
            time.sleep(5)
            
        except Exception as e:
            print(f"Failed to publish: {e}")
            
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
