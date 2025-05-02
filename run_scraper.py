from flask import Flask
from scraper import scrape_site, scrape_site_with_selenium
from db_manager import db
import time
from app import SITES_TO_SCRAPE
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import threading
from datetime import datetime

def open_browser_session():
    """Opens browser sessions for specific sites and keeps them open for 10 minutes"""
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--user-data-dir=/root/.config/google-chrome")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-popup-blocking")
    
    service = Service("/usr/local/bin/chromedriver")
    
    # Open browsers for each site
    drivers = []
    sites = ['https://avenoel.org', 'https://onche.org']
    
    for site in sites:
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            # Allow redirects by configuring the driver
            driver.execute_cdp_cmd('Page.setBypassCSP', {'enabled': True})
            driver.get(site)
            drivers.append(driver)
            print(f"[INFO] Opened browser session for {site}")
        except Exception as e:
            print(f"[ERROR] Failed to open browser for {site}: {e}")
    
    # Keep browsers open for 10 minutes
    time.sleep(600)
    
    # Close all browsers
    for driver in drivers:
        try:
            driver.quit()
        except Exception as e:
            print(f"[ERROR] Failed to close browser: {e}")
    
    print("[INFO] Closed all browser sessions")

def run_scraper():
    app = Flask(__name__)
    
    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/scraped_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Track when we last opened browser sessions
    last_browser_session = datetime.now()

    with app.app_context():
        while True:
            print("[INFO] Starting scrape cycle...")
            
            # Check if an hour has passed since last browser session
            current_time = datetime.now()
            if (current_time - last_browser_session).total_seconds() >= 3600:  # 1 hour = 3600 seconds
                print("[INFO] Starting browser sessions")
                # Start browser sessions in a separate thread
                browser_thread = threading.Thread(target=open_browser_session)
                browser_thread.start()
                last_browser_session = current_time
            
            for site_key, site_config in SITES_TO_SCRAPE.items():
                if site_key in ['jeuxvideo', '2sucres', 'onche', 'avenoel']:
                    print(f"[INFO] Using Selenium for site: {site_key}")
                    scrape_site_with_selenium(site_key, site_config)
                else:
                    print(f"[INFO] Using scrap for site: {site_key}")
                    scrape_site(site_key, site_config)
            print("[INFO] Scrape cycle completed. Waiting 60 seconds...")
            time.sleep(60)

if __name__ == '__main__':
    try:
        run_scraper()
    except KeyboardInterrupt:
        print("[INFO] Scraper process stopped")