import requests
from sqlalchemy import func
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_manager import db, Topic
import time

from forums.jeuxvideo import parse_jeuxvideo
from forums.village import parse_village
from forums.avenoel import parse_avenoel
from forums.onche import parse_onche
from forums.sucres import parse_2sucres

def scrape_site(site_key, site_config):
    """
    Fetch a site and parse its content according to the site's configuration.
    """
    url = site_config['url']
    parser_func_name = site_config['parser']

    print(f"[DEBUG] Scraping site: {site_key} - URL: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': url,
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Get the content encoding from headers
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        print(f"[DEBUG] Content-Encoding: {content_encoding}")

        if 'br' in content_encoding:
            print("[DEBUG] Decompressing Brotli response")
            try:
                import brotli
                response_text = brotli.decompress(response.content).decode('utf-8')
            except Exception as e:
                print(f"[ERROR] Brotli decompression failed, trying raw content: {e}")
                response_text = response.content.decode('utf-8', errors='replace')
        elif 'gzip' in content_encoding:
            print("[DEBUG] Decompressing GZIP response")
            response_text = response.text  # requests automatically handles gzip
        else:
            print("[DEBUG] No decompression needed")
            response_text = response.text

        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")

    except requests.RequestException as e:
        print(f"[ERROR] Unable to scrape {url}: {e}")
        return

    parser_func = globals().get(parser_func_name)
    if not parser_func:
        print(f"[ERROR] Parser function '{parser_func_name}' not found.")
        return

    # Parse the HTML content
    try:
        topics = parser_func(response_text)  # Use HTML content for other sites
    except Exception as e:
        print(f"[ERROR] Failed to parse HTML for site {site_key}: {e}")
        return

    print(f"[DEBUG] Parsed {len(topics)} topics for site: {site_key}")

    # Save topics to the database
    for topic in topics:
        print(f"[DEBUG] Processing topic: {topic['title']} - URL: {topic['topic_url']}")
        existing_topic = Topic.query.filter_by(topic_url=topic['topic_url']).first()
        if not existing_topic:
            new_topic = Topic(
                site_key=site_key,
                title=topic['title'],
                topic_url=topic['topic_url'],
                username=topic['username'],
                replies=int(topic['replies']),
                last_activity=topic['last_activity'],
                timestamp=datetime.now(timezone.utc)  # Use timezone-aware UTC datetime
            )
            db.session.add(new_topic)
        else:
            # Update existing topic if needed
            existing_topic.title = topic['title']
            existing_topic.username = topic['username']
            existing_topic.replies = int(topic['replies'])
            existing_topic.last_activity = topic['last_activity']
            existing_topic.timestamp = datetime.now(timezone.utc)
            db.session.add(existing_topic)
            print(f"[DEBUG] Topic already exists in the database: {topic['topic_url']}")
    db.session.commit()
    print(f"[DEBUG] Finished saving topics for site: {site_key}")


def scrape_site_with_selenium(site_key, site_config):
    """
    Fetch a site using Selenium and parse its content according to the site's configuration.
    """
    url = site_config['url']
    parser_func_name = site_config['parser']

    print(f"[DEBUG] Scraping site with Selenium: {site_key} - URL: {url}")

    # Configure Selenium WebDriver for containerized environment
    chrome_options = Options()

    # Container-specific Chrome options
    chrome_options.binary_location = "/usr/bin/google-chrome"
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--user-data-dir=/root/.config/google-chrome")
    chrome_options.add_argument("--profile-directory=Default")

    # Use the ChromeDriver installed in the container
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the page
        driver.get(url)

        time.sleep(10)

        # Wait for the JavaScript-rendered content to load (if applicable)
        if site_key == '2sucres':
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.tbody > div > div.tr"))
            )

        # Get the page source and parse it with BeautifulSoup
        html_content = driver.page_source
        parser_func = globals().get(parser_func_name)
        if not parser_func:
            print(f"[ERROR] Parser function '{parser_func_name}' not found.")
            return

        topics = parser_func(html_content)
        print(f"[DEBUG] Parsed {len(topics)} topics for site: {site_key}")

        # Save topics to the database
        for topic in topics:
            print(f"[DEBUG] Processing topic: {topic['title']} - URL: {topic['topic_url']}")
            existing_topic = Topic.query.filter_by(topic_url=topic['topic_url']).first()
            if not existing_topic:
                new_topic = Topic(
                    site_key=site_key,
                    title=topic['title'],
                    topic_url=topic['topic_url'],
                    username=topic['username'],
                    replies=int(topic['replies']),
                    last_activity=topic['last_activity'],
                    timestamp=datetime.now(timezone.utc)  # Use timezone-aware UTC datetime
                )
                db.session.add(new_topic)
            else:
                print(f"[DEBUG] Topic already exists in the database: {topic['topic_url']}")
                # Update existing topic if needed
                existing_topic.title = topic['title']
                existing_topic.username = topic['username']
                existing_topic.replies = int(topic['replies'])
                existing_topic.last_activity = topic['last_activity']
                existing_topic.timestamp = datetime.now(timezone.utc)
                db.session.add(existing_topic)

        db.session.commit()
        print(f"[DEBUG] Finished saving topics for site: {site_key}")

    except Exception as e:
        print(f"[ERROR] Failed to scrape {url} with Selenium: {e}")
    finally:
        driver.quit()
