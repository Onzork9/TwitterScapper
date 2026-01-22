import os
import random
import time
import undetected_chromedriver as uc
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from fp.fp import FreeProxy 
import sqlite3

class WebBot:
    def __init__(self, headless=False, download_location=None):
        self.headless = headless
        self.download_location = download_location or os.getcwd()
        self._driver = None
        self.alldata = {}
        # Initialize Database connection - MUST be here
        self.db_conn = self.init_db()

    def init_db(self):
        """Creates tables if they don't exist: users, tweets, and hashtags."""
        conn = sqlite3.connect("market_data.db")
        cursor = conn.cursor()
        # 1. Users table (Unique handles)
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            display_name TEXT
        )''')
        # 2. Tweets table
        cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (
            tweet_id INTEGER PRIMARY KEY,
            username TEXT,
            content TEXT,
            search_keyword TEXT,
            tweet_url TEXT,
            timestamp INTEGER,
            views INTEGER, comments INTEGER, reposts INTEGER, likes INTEGER, bookmarks INTEGER,
            FOREIGN KEY (username) REFERENCES users (username)
        )''')
        # 3. Hashtags table (Normalized for many-to-many relationship)
        cursor.execute('''CREATE TABLE IF NOT EXISTS hashtags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER,
            tag TEXT,
            FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id)
        )''')
        conn.commit()
        return conn
    

    def _get_free_proxy(self):
        """Fetches a high-anonymity proxy."""
        try:
            return FreeProxy(https=True, anonym=True, elite=True).get()
        except:
            return None

    def init_driver(self, use_proxy=True):
        """Initializes an undetected Chrome instance."""
        options = uc.ChromeOptions()
        
        # UC handles most stealth settings automatically, 
        # but we can add our custom ones:
        if self.headless:
            # UC works best with the 'new' headless mode
            options.add_argument("--headless") 
            
        if use_proxy:
            proxy = self._get_free_proxy()
            if proxy:
                print(f"Using Proxy: {proxy}")
                options.add_argument(f'--proxy-server={proxy}')

        # Add custom profile/download settings
        options.add_argument(f"--user-data-dir={os.path.join(os.getcwd(), 'chrome_profile')}")
        
        # Preferences are handled slightly differently in UC
        prefs = {
            "download.default_directory": self.download_location,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)

        # Initialize the driver (UC handles its own chromedriver installation)
        self._driver = uc.Chrome(options=options, version_main=131) # Ensure version matches your Chrome

        return self._driver

    def get_trending_report(self):
        cursor = self.db_conn.cursor()
        query = """
        SELECT h.tag, COUNT(h.tag) as frequency, SUM(t.likes) as total_likes
        FROM hashtags h
        JOIN tweets t ON h.tweet_id = t.tweet_id
        GROUP BY h.tag
        ORDER BY total_likes DESC
        LIMIT 5;
        """
        cursor.execute(query)
        print("\n--- Market Trends Report ---")
        for row in cursor.fetchall():
            print(f"Tag: #{row[0]} | Appearances: {row[1]} | Total Likes: {row[2]}")


    def logout_x(self):
        self._driver.get('https://x.com/logout')
        time.sleep(random.uniform(2, 4))
        buttons = self._driver.find_elements(By.XPATH, "//button[contains(@role, 'button')]")
        for btn in buttons:
            if btn.text.lower() == 'log out':
                btn.click()
                print(f"Successfully Logged Out")
                break

    def process_flow(self):
        self.login_to_x()
        
        total_goal = 2000
        search_query_list = ['#nifty50', '#sensex']
        
        # Corrected: Divide by the number of keywords in the list
        limit_per_keyword = total_goal // len(search_query_list) 
        
        for search_words in search_query_list:
            print(f"Starting search for {search_words}. Target for this keyword: {limit_per_keyword}")
            
            time.sleep(random.uniform(1, 3))
            
            # Pass the calculated limit to your search_query method
            self.search_query(search_words, limit_per_keyword)
            
            # Navigate back home to reset the UI state
            self._driver.get('https://x.com/home')
            time.sleep(random.uniform(3, 5))
            
        self.logout_x()
        time.sleep(random.uniform(2, 5))
        

    def login_to_x(self):
        """Example of finding the username field on X using text-based XPATH."""
        self._driver.get("https://x.com/i/flow/login")
        
        # Give the page a moment to load its complex Javascript
        time.sleep(9) 
        username = 'akhilsharma31820@gmail.com'
        try:
            # X uses 'name' attributes, but here is how you find it by text logic
            # This looks for an input where the label or placeholder contains 'Phone, email, or username'
            user_input = self._driver.find_element(By.XPATH, "//input[contains(@autocomplete, 'username')]")
            user_input.click()
            user_input.send_keys(username)
            user_input.send_keys(Keys.ENTER)
            print(f"Successfully entered: {username}")
            
            time.sleep(6)
            
            username_input_head = self._driver.find_element(By.XPATH, "//h1[contains(@role, 'heading')]")
            if 'enter your phone number or username' == username_input_head.text.lower():
                
                username_input = self._driver.find_element(By.XPATH, "//input[contains(@name, 'text')]")
                username_input.click()
                username_input.send_keys('@akhil_shar46999')
                username_input.send_keys(Keys.ENTER)
                time.sleep(4.5)
            
            user_pasword = self._driver.find_element(By.XPATH, "//input[contains(@type, 'password')]")
            user_pasword.click()
            user_pasword.send_keys('Akhil@2000')
            user_pasword.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"Could not find login field: {e}")

    def format_metric(self, text):
        """Converts '13K', '1.2M', etc. to integers."""
        if not text or text.strip() == "":
            return 0
        text = text.upper().replace(',', '').strip()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        if text[-1] in multipliers:
            return int(float(text[:-1]) * multipliers[text[-1]])
        try:
            return int(float(text))
        except ValueError:
            return 0
        
    def search_query(self, search_keyword, limit_per_keyword):
        try:
            wait = WebDriverWait(self._driver, 15)
            processed_ids = set() # Track IDs handled in THIS session
            self.total_tweets = 0 # Counter for the while loop
            target_limit = limit_per_keyword # Set your desired tweet limit here

            # 1. Search Logic
            keyword_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="Search"]')
            ))
            keyword_input.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            keyword_input.send_keys(search_keyword, Keys.ENTER)

            # 2. Switch to 'Latest' tab
            latest_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Latest']")))
            self._driver.execute_script("arguments[0].click();", latest_tab)
            time.sleep(3)

            main_window = self._driver.current_window_handle
            self._driver.switch_to.new_window("tab")
            second_tab = self._driver.current_window_handle
            self._driver.switch_to.window(main_window)

            # 3. Scroll & Scrape Loop
            while self.total_tweets < target_limit:
                post_list = self._driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'cellInnerDiv')]")
                
                for post in post_list:
                    if self.total_tweets >= target_limit: break
                    
                    try:
                        links = post.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
                        if not links: continue

                        post_link = links[0].get_attribute("href")
                        tweet_id = post_link.split('/')[-1]

                        # Skip if we already handled it in this loop OR if it's in the DB
                        if tweet_id in processed_ids:
                            continue
                        
                        # Switch to reusable tab and scrape
                        self._driver.switch_to.window(second_tab)
                        self._driver.get(post_link)
                        
                        # Note: Ensure scrape_process returns True if successful
                        success = self.scrape_process(search_keyword)
                        
                        if success:
                            self.total_tweets += 1 # Increments only when True is returned
                            print(f"Progress: {self.total_tweets} tweets stored.")
                        else:
                            time.sleep(random.uniform(25, 35))


                        self._driver.switch_to.window(main_window)
                        time.sleep(random.uniform(1, 2))

                    except Exception as e:
                        print(f"Error: {e}")
                        self._driver.switch_to.window(main_window)

                # 4. Scroll down after checking currently visible posts
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) # Wait for new content to load

            # 5. Cleanup
            self._driver.switch_to.window(second_tab)
            self._driver.close()
            self._driver.switch_to.window(main_window)

        except Exception as e:
            print(f"Critical error: {e}")
            
    def scrape_process(self, search_keyword):
        try:
            tweet_url = self._driver.current_url
            try:
                tweet_id = int(tweet_url.split('/')[-1])
            except (ValueError, IndexError): return False

            # CHECK DB INSTEAD OF DICTIONARY
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT tweet_id FROM tweets WHERE tweet_id=?", (tweet_id,))
            if cursor.fetchone():
                print(f"Skipping: Tweet {tweet_id} already in DB.")
                return False

            name_elements = self._driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'User-Name')]")
            if not name_elements: return False
            
            # Extract data
            full_name_text = name_elements[0].text
            display_name = full_name_text.split('\n')[0]
            username = full_name_text.split('\n')[-1]
            
            # Re-normalize username if it's a relative time (like '59m')
            if not username.startswith('@'):
                username = f"@{tweet_url.split('/')[-3]}"

            content_elements = self._driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'tweetText')]")
            tweet_content = content_elements[0].text if content_elements else ""
            timestamp_ms = (tweet_id >> 22) + 1288834974657
            
            # Metrics
            engagement_elements = self._driver.find_elements(By.XPATH, "//span[contains(@data-testid, 'app-text-transition-container')]")
            m = [self.format_metric(el.text) for el in engagement_elements]
            # Ensure we have 5 values even if X hides some
            m += [0] * (5 - len(m))

            # --- NORMALIZED DB INSERTION ---
            # 1. Insert User
            cursor.execute("INSERT OR IGNORE INTO users (username, display_name) VALUES (?, ?)", (username, display_name))
            
            # 2. Insert Tweet
            cursor.execute('''INSERT INTO tweets VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                           (tweet_id, username, tweet_content, search_keyword, tweet_url, timestamp_ms, m[0], m[1], m[2], m[3], m[4]))
            
            # 3. Insert Hashtags
            hashtags = re.findall(r"#(\w+)", tweet_content)
            for tag in set(hashtags):
                cursor.execute("INSERT INTO hashtags (tweet_id, tag) VALUES (?, ?)", (tweet_id, tag.lower()))
            
            self.db_conn.commit()
            print(f"Successfully saved to DB: {tweet_id}")
            return True
        except Exception as e:
            print(f"Error during scrape_process: {e}")
            return False

if __name__ == "__main__":
    # 1. Initialize the bot
    bot = WebBot(headless=False)
    
    try:
        # 2. Start the browser
        # Note: Set use_proxy=True if you want to use the FreeProxy logic
        bot.init_driver(use_proxy=False) 

        # 3. Run the main automation flow
        bot.process_flow()
        
        # 4. Generate the Trends Report from the DB
        bot.get_trending_report()

    except KeyboardInterrupt:
        print("\nBot stopped manually by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 5. Cleanup: Ensure driver and DB close properly
        if bot._driver:
            bot._driver.quit()
        if hasattr(bot, 'db_conn'):
            bot.db_conn.close()
            print("Database connection closed.")