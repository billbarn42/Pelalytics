import os
import time
import sqlite3
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

DB_PATH = "peloton_classes.db"
BASE_URL = "https://members.onepeloton.com/classes/cycling"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def get_credentials():
    email = os.environ.get("PELOTON_EMAIL")
    password = os.environ.get("PELOTON_PASSWORD")
    if not email or not password:
        raise Exception("PELOTON_EMAIL and PELOTON_PASSWORD must be set in your environment or .env file.")
    return email, password

def init_driver(headless=False):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login(driver, email, password):
    driver.get("https://members.onepeloton.com/login")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "usernameOrEmail")))
    driver.find_element(By.ID, "usernameOrEmail").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    WebDriverWait(driver, 30).until(lambda d: "/home" in d.current_url or "/overview" in d.current_url or "/classes" in d.current_url)

def extract_first_powerzone_class(driver):
    """
    Extract data from the first Power Zone class found in search results.
    """
    print("[INFO] Navigating to classes page...")
    driver.get(BASE_URL)
    try:
        print("[INFO] Searching for 'power zone'...")
        search_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='searchBar']"))
        )
        search_input.clear()
        search_input.send_keys("power zone")
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)
        print("[INFO] Search submitted, waiting for results...")
    except Exception as e:
        print(f"[ERROR] Could not use search bar: {e}")
        return None
    try:
        print("[INFO] Looking for the first class tile...")
        first_tile = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='videoCell']"))
        )
        print(f"[INFO] Found class tile, extracting title...")
        # Extract title from the tile directly
        title = first_tile.find_element(By.CSS_SELECTOR, "[data-test-id='videoCellTitle']").text
        print(f"[INFO] Class title: {title}")
        # Click the tile to open details modal
        first_tile.click()
        time.sleep(2)
        print("[INFO] Clicked on class tile, waiting for modal...")
        # Wait for modal to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='classDetailsTitle']"))
        )
        # Get the class URL (will include classId in query params)
        class_url = driver.current_url
        print(f"[INFO] Class URL: {class_url}")
        
        # Extract class name from the details page
        try:
            title = driver.find_element(By.CSS_SELECTOR, "[data-test-id='classDetailsTitle']").text
            print(f"[INFO] Class title from details page: {title}")
        except Exception as e:
            print(f"[WARN] Could not get title from details page, using tile title: {e}")
        
        # Extract duration from title (e.g., "45 min" from "45 min Power Zone Classic Rock Ride")
        duration = None
        try:
            duration = int(title.split()[0])
            print(f"[INFO] Duration: {duration} minutes")
        except Exception as e:
            print(f"[WARN] Could not extract duration from title: {e}")
        
        # Extract difficulty rating (look for a span with a decimal number)
        rating = None
        try:
            # Find all span elements and look for one with a decimal rating
            spans = driver.find_elements(By.TAG_NAME, "span")
            for span in spans:
                text = span.text.strip()
                # Look for a decimal number between 0 and 10
                if text and '.' in text and '+' not in text:
                    try:
                        test_rating = float(text)
                        if 0 <= test_rating <= 10:
                            rating = test_rating
                            print(f"[INFO] Difficulty rating: {rating}")
                            break
                    except ValueError:
                        continue
            
            if rating is None:
                print(f"[WARN] Could not find difficulty rating element")
        except Exception as e:
            print(f"[WARN] Could not get difficulty rating: {e}")
            import traceback
            traceback.print_exc()
        
        # Extract instructor name
        instructor = ""
        try:
            instructor_elem = driver.find_element(By.CSS_SELECTOR, "[data-test-id='classDetailsSubtitle']")
            instructor = instructor_elem.text.split('·')[0].strip()
            print(f"[INFO] Instructor: {instructor}")
        except Exception as e:
            print(f"[WARN] Could not get instructor: {e}")
        air_time = ""
        class_info = {
            "id": class_url.split("/")[-1],
            "title": title,
            "instructor": instructor,
            "duration_minutes": duration,
            "difficulty_rating": rating,
            "class_type": "Power Zone",
            "original_air_time": air_time,
            "url": class_url
        }
        print(f"[FOUND] {title} | {instructor} | {duration} min | {air_time} | {class_url} | Rating: {rating}")
        return class_info
    except Exception as e:
        print(f"[ERROR] Could not find or process first class tile: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_class_to_db(cls):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY,
        title TEXT,
        instructor TEXT,
        duration_minutes INTEGER,
        difficulty_rating REAL,
        class_type TEXT,
        original_air_time TEXT,
        url TEXT
    )
    """)
    # Check if record exists
    c.execute("SELECT id FROM classes WHERE id = ?", (cls["id"],))
    exists = c.fetchone()
    
    c.execute("""
    INSERT OR REPLACE INTO classes
    (id, title, instructor, duration_minutes, difficulty_rating, class_type, original_air_time, url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cls["id"], cls["title"], cls["instructor"], cls["duration_minutes"],
        cls["difficulty_rating"], cls["class_type"], cls["original_air_time"], cls["url"]
    ))
    action = "UPDATED" if exists else "INSERTED"
    print(f"[DB {action}] {cls['title']} | {cls['instructor']} | {cls['duration_minutes']} min | Rating: {cls['difficulty_rating']}")
    conn.commit()
    conn.close()

def wait_for_modal_and_get(driver):
    """Wait for class details modal to stabilize, then return fresh references.
    Returns dict with title, instructor, duration, rating. Raises TimeoutException on failure.
    """
    WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='classDetailsTitle']"))
    )
    # Re-find elements inside modal to avoid stale references
    title = driver.find_element(By.CSS_SELECTOR, "[data-test-id='classDetailsTitle']").text.strip()
    # Instructor line may be missing the dot separator for legacy classes
    instructor = ""
    try:
        sub = driver.find_element(By.CSS_SELECTOR, "[data-test-id='classDetailsSubtitle']").text.strip()
        instructor = sub.split('·')[0].strip() if '·' in sub else sub
    except Exception:
        instructor = ""

    # Duration: prefer explicit badge/pill; fallback to parse from title
    duration = None
    try:
        pill = driver.find_element(By.XPATH, "//span[contains(., 'min')]")
        # Extract leading integer
        import re
        m = re.search(r"(\d{2,}|\d)\s*min", pill.text)
        if m:
            duration = int(m.group(1))
    except Exception:
        pass
    if duration is None:
        try:
            duration = int(title.split()[0])
        except Exception:
            duration = None

    # Difficulty rating: look for a decimal number element, legacy variants included
    rating = None
    try:
        spans = driver.find_elements(By.TAG_NAME, "span")
        for span in spans:
            t = span.text.strip()
            if t and '.' in t and '+' not in t:
                try:
                    val = float(t)
                    if 0 <= val <= 10:
                        rating = val
                        break
                except ValueError:
                    continue
    except Exception:
        rating = None
    return {
        "title": title,
        "instructor": instructor,
        "duration": duration,
        "rating": rating,
    }

def scrape_via_details_page(driver, class_id):
    """Fallback: open the class details modal via URL, then scrape it, closing afterward."""
    details_url = f"{BASE_URL}?modal=classDetailsModal&classId={class_id}"
    driver.execute_script("window.open(arguments[0])", details_url)
    driver.switch_to.window(driver.window_handles[-1])
    try:
        data = wait_for_modal_and_get(driver)
        return data
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def extract_powerzone_classes(driver, max_classes=10, start_date=None, end_date=None, oldest_first=False):
    """
    Extract data from multiple Power Zone classes found in search results.
    Returns a list of class dictionaries.
    
    Args:
        driver: Selenium WebDriver instance
        max_classes: Maximum number of classes to extract
        start_date: Start date filter (datetime object or None)
        end_date: End date filter (datetime object or None)
        oldest_first: If True, sort oldest to newest (efficient for historical scraping)
    """
    try:
        print("[INFO] Navigating to classes page...")
        # Build URL with sort order
        url = BASE_URL
        if oldest_first:
            url += "?sort=original_air_time&desc=false"
            print("[INFO] Using oldest-first sort order")
        
        driver.get(url)
        time.sleep(3)
    except Exception as e:
        print(f"[ERROR] Could not navigate to classes page: {e}")
        return []
    
    # Use filters instead of search to access all classes
    try:
        print("[INFO] Opening filter menu...")
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='filterButton']"))
        )
        filter_button.click()
        time.sleep(2)
        
        print("[INFO] Clicking on 'Class Type' accordion...")
        class_type_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id='accordion-button-ClassType']"))
        )
        class_type_button.click()
        time.sleep(1)
        
        print("[INFO] Selecting 'Power Zone' filter...")
        # Find the Power Zone option by text content
        power_zone_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Power Zone')]]"))
        )
        power_zone_button.click()
        time.sleep(2)
        
        # Close the filter panel using the close button
        print("[INFO] Closing filter panel...")
        close_filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='filterCloseButton']"))
        )
        close_filter_button.click()
        time.sleep(2)
        
        print("[INFO] Power Zone filter applied, waiting for results...")
    except Exception as e:
        print(f"[ERROR] Could not apply filters: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    classes = []
    processed_ids = set()
    classes_outside_range = 0
    consecutive_skips = 0
    found_range_start = False  # Track if we've entered the date range
    skip_increment = 1  # How many tiles to skip during fast-forward
    stale_element_errors = 0  # Track DOM staleness
    max_stale_errors = 5  # Stop after this many stale errors
    
    # Calculate intelligent skip increment based on:
    # 1. How many months we need to traverse
    # 2. The class density of the period we're scrolling through
    # NOTE: This initial skip is just a first attempt - we'll adjust as we check dates
    if start_date or end_date:
        from datetime import datetime
        now = datetime.now()
        
        # Determine which boundary we're skipping past during fast-forward
        if oldest_first:
            # Scrolling from oldest, fast-forward BEFORE start_date
            # So we're skipping from oldest available up to start_date
            target_date = start_date
            months_to_skip = abs((target_date.year - 2019) * 12 + target_date.month)  # From 2019 (earliest)
        else:
            # Scrolling from newest (default), fast-forward AFTER end_date
            # So we're skipping from now back to end_date
            if end_date:
                months_to_skip = abs((now.year - end_date.year) * 12 + (now.month - end_date.month))
            else:
                # No end_date, use start_date
                months_to_skip = abs((now.year - start_date.year) * 12 + (now.month - start_date.month))
        
        # Estimate class density: use current year's density (2024+: ~27/month average)
        # Skip ~80% of estimated classes to be safe
        estimated_classes = months_to_skip * 27
        skip_increment = max(1, int(estimated_classes * 0.8))
        
        print(f"[INFO] Estimated {months_to_skip} months to skip (~{estimated_classes} classes)")
        print(f"[INFO] Using skip increment of {skip_increment} tiles during fast-forward phase")
    
    i = 0
    while i < max_classes:
        try:
            print(f"\n[INFO] Looking for class tile #{i+1}...")
            
            # Get all class tiles currently loaded
            tiles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test-id='videoCell']"))
            )
            
            # If we need a tile that's not loaded yet, scroll to load more
            while i >= len(tiles):
                print(f"[INFO] Need tile #{i+1} but only {len(tiles)} loaded. Scrolling...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Re-fetch tiles
                new_tiles = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='videoCell']")
                if len(new_tiles) == len(tiles):
                    # No new tiles loaded
                    print(f"[INFO] No more classes available (found {len(tiles)} total)")
                    break
                tiles = new_tiles
            
            if i >= len(tiles):
                # Still don't have enough tiles
                print(f"[INFO] Reached end of available classes")
                break
            
            # Scroll the specific tile into view
            tile = tiles[i]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tile)
            time.sleep(0.5)
            
            # Extract date from tile BEFORE opening (format: "Tue 11/25/25 @ 1:00 PM")
            try:
                date_elem = tile.find_element(By.CSS_SELECTOR, "div.sc-fOlkSH")
                date_text = date_elem.text.strip()
                print(f"[INFO] Class date from tile: {date_text}")
                
                # Parse date (format: "Tue 11/25/25 @ 1:00 PM")
                date_part = date_text.split('@')[0].strip().split()[-1]  # Get "11/25/25"
                class_date = datetime.strptime(date_part, '%m/%d/%y')
                
                # DYNAMIC SKIP RECALCULATION during fast-forward
                # If we're not in range yet, recalculate skip based on current position
                if not found_range_start:
                    if oldest_first:
                        # Fast-forwarding before start_date
                        if start_date and class_date < start_date:
                            months_remaining = abs((start_date.year - class_date.year) * 12 + (start_date.month - class_date.month))
                            if months_remaining > 0:
                                skip_increment = max(1, int(months_remaining * 27 * 0.8))
                                print(f"[INFO] Class date {class_date.strftime('%Y-%m-%d')} is before start date")
                                print(f"[INFO] ~{months_remaining} months to go, recalculated skip to {skip_increment} tiles")
                                classes_outside_range += 1
                                i += skip_increment
                                continue
                    else:
                        # Fast-forwarding after end_date (default newest->oldest)
                        if end_date and class_date > end_date:
                            months_remaining = abs((class_date.year - end_date.year) * 12 + (class_date.month - end_date.month))
                            if months_remaining > 0:
                                skip_increment = max(1, int(months_remaining * 27 * 0.8))
                                print(f"[INFO] Class date {class_date.strftime('%Y-%m-%d')} is after end date")
                                print(f"[INFO] ~{months_remaining} months to go, recalculated skip to {skip_increment} tiles")
                                classes_outside_range += 1
                                i += skip_increment
                                continue
                        
                        # OVERSHOT: We went too far (before start_date in newest->oldest)
                        if start_date and class_date < start_date:
                            print(f"[INFO] ⚠️ Overshot! Class date {class_date.strftime('%Y-%m-%d')} is before start date")
                            print(f"[INFO] Backing up to find range start...")
                            # Back up by 20 tiles at a time
                            i = max(0, i - 20)
                            continue
                
                # Check if we're in the target date range
                in_range = True
                if start_date and class_date < start_date:
                    in_range = False
                if end_date and class_date > end_date:
                    in_range = False
                
                # If we just entered the range, mark it and ensure we're at the start
                if in_range and not found_range_start:
                    print(f"[INFO] ✓ Entered date range at tile {i}! Date: {class_date.strftime('%Y-%m-%d')}")
                    found_range_start = True
                    # Back up by 20 to ensure we catch the very first class in range
                    i = max(0, i - 20)
                    print(f"[INFO] Backing up 20 tiles to ensure we catch range start...")
                    continue
                
                # Now handle based on whether we're in range or not
                if oldest_first:
                    if end_date and class_date > end_date:
                        print(f"[INFO] Class date {class_date.strftime('%Y-%m-%d')} is after end date")
                        print(f"[INFO] Reached end of date range (oldest-first), stopping...")
                        break
                else:
                    if start_date and class_date < start_date:
                        print(f"[INFO] Class date {class_date.strftime('%Y-%m-%d')} is before start date")
                        consecutive_skips += 1
                        if found_range_start and consecutive_skips >= 10:
                            print(f"[INFO] Reached 10 consecutive classes before start date, stopping...")
                            break
                        i += 1
                        continue
                
                # We're in range and ready to process!
                if not in_range:
                    # Should not get here, but just in case
                    i += 1
                    continue
                    
                found_range_start = True
                consecutive_skips = 0
                print(f"[INFO] ✓ Class date {class_date.strftime('%Y-%m-%d')} is in range, extracting details...")
                
            except Exception as e:
                print(f"[WARN] Could not extract date from tile: {e}, will process anyway")
                class_date = None
            
            # Extract title from the tile directly
            title = tile.find_element(By.CSS_SELECTOR, "[data-test-id='videoCellTitle']").text
            print(f"[INFO] Class title: {title}")
            
            # Click the tile to open details modal and use robust waits
            tile.click()
            print("[INFO] Clicked on class tile, waiting for modal...")
            modal_data = None
            try:
                modal_data = wait_for_modal_and_get(driver)
            except (TimeoutException, StaleElementReferenceException):
                print("[WARN] Modal elements not stable; attempting details-page fallback...")
            
            # Get the class URL (will include classId in query params)
            class_url = driver.current_url
            class_id = class_url.split("classId=")[-1].split("&")[0] if "classId=" in class_url else class_url.split("/")[-1]
            if modal_data is None:
                # Try scraping via details page as a fallback path
                try:
                    modal_data = scrape_via_details_page(driver, class_id)
                except Exception as e:
                    print(f"[ERROR] Details-page fallback failed: {e}")
            
            # Skip if already processed
            if class_id in processed_ids:
                print(f"[INFO] Class {class_id} already processed, skipping...")
                # Close modal
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
                continue
            
            processed_ids.add(class_id)
            print(f"[INFO] Class URL: {class_url}")
            
            # Use modal_data collected via robust path
            title = modal_data.get("title") or title
            instructor = modal_data.get("instructor", "")
            duration = modal_data.get("duration")
            rating = modal_data.get("rating")
            if title:
                print(f"[INFO] Class title from details page: {title}")
            if duration is not None:
                print(f"[INFO] Duration: {duration} minutes")
            else:
                print("[WARN] Duration not found")
            if rating is not None:
                print(f"[INFO] Difficulty rating: {rating}")
            else:
                print("[WARN] Could not find difficulty rating element")
            if instructor:
                print(f"[INFO] Instructor: {instructor}")
            
            # Format air_time from class_date if available
            air_time = ""
            if class_date:
                air_time = class_date.strftime('%Y-%m-%d')
            
            class_info = {
                "id": class_id,
                "title": title,
                "instructor": instructor,
                "duration_minutes": duration,
                "difficulty_rating": rating,
                "class_type": "Power Zone",
                "original_air_time": air_time,
                "url": class_url
            }
            print(f"[FOUND] {title} | {instructor} | {duration} min | Rating: {rating}")
            classes.append(class_info)
            
            # Close the modal by clicking the close button
            try:
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='closeModalButton']"))
                )
                close_button.click()
                time.sleep(1)
                print("[INFO] Modal closed, moving to next class...")
            except Exception as e:
                print(f"[WARN] Could not close modal: {e}")
                # Fallback: press ESC
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except Exception:
                    pass
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Could not process class tile #{i+1}: {e}")
            
            # Check for stale element errors
            if "stale element" in error_msg.lower() or "stale element reference" in error_msg.lower():
                stale_element_errors += 1
                print(f"[WARN] Stale element error detected ({stale_element_errors}/{max_stale_errors})")
                
                if stale_element_errors >= max_stale_errors:
                    print(f"\n{'='*60}")
                    print(f"[ERROR] Browser DOM has become stale after {i} classes")
                    print(f"{'='*60}")
                    print(f"This happens after processing many classes in one session.")
                    print(f"")
                    print(f"✅ Successfully saved {len(classes)} classes to database")
                    print(f"")
                    print(f"💡 To continue from where you left off, note the last")
                    print(f"   processed date and adjust your --start-date accordingly.")
                    print(f"")
                    print(f"   Or use batch_scrape.py to handle large date ranges")
                    print(f"   automatically with monthly chunks.")
                    print(f"{'='*60}")
                    break
            
            import traceback
            traceback.print_exc()
            # Try to close modal if it's open
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, "[data-test-id='closeModalButton']")
                close_button.click()
                time.sleep(1)
            except Exception:
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except Exception:
                    pass
        
        # Normal increment after processing a class
        i += 1
    
    return classes

def main():
    parser = argparse.ArgumentParser(description='Scrape Peloton Power Zone classes')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-classes', type=int, default=None, help='Maximum number of classes to scrape (optional, defaults to all classes in date range)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode (faster)')
    parser.add_argument('--oldest-first', action='store_true', help='Sort oldest to newest (useful for historical scraping)')
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            print(f"[ERROR] Invalid start date format: {args.start_date}. Use YYYY-MM-DD")
            return
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            print(f"[ERROR] Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            return
    
    # Set default max_classes based on whether date range is provided
    max_classes = args.max_classes
    if max_classes is None:
        if start_date or end_date:
            max_classes = 10000  # High limit for date-filtered scraping
            print(f"[INFO] No max-classes specified, will scrape all classes in date range")
        else:
            max_classes = 10  # Conservative default when no dates specified
            print(f"[INFO] No date range or max-classes specified, defaulting to {max_classes} classes")
    
    # Auto-detect sort order for efficiency
    oldest_first = args.oldest_first
    if not oldest_first and start_date:
        # If scraping old classes (before 2023), auto-enable oldest-first
        # Volume ramped up significantly in 2023 (~25-30 classes/month)
        if start_date.year < 2023:
            oldest_first = True
            print(f"[INFO] Auto-enabling oldest-first sort (scraping pre-2023 classes)")
    
    load_dotenv()
    email, password = get_credentials()
    driver = None
    try:
        driver = init_driver(headless=args.headless)
        login(driver, email, password)
        print("[INFO] Login successful.")
        
        # Extract multiple classes with optional date filters
        classes = extract_powerzone_classes(driver, max_classes=max_classes, 
                                           start_date=start_date, end_date=end_date,
                                           oldest_first=oldest_first)
        
        if classes:
            print(f"\n[INFO] Found {len(classes)} classes, saving to database...")
            for class_info in classes:
                save_class_to_db(class_info)
            print(f"[INFO] {len(classes)} classes saved to database.")
        else:
            print("[INFO] No classes found or saved.")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        print("[INFO] Script complete.")

if __name__ == "__main__":
    main()
