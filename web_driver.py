from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import *
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager


def initialize_driver():
    try:
        print("Initializing driver...")
        chrome_options = Options()
        window_size = f"{WIDTH},{HEIGHT}"
        print(f"Window Size: {window_size}")
        if HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--window-size={window_size}")
        # service = Service(chromedriver_path)
        driver = webdriver.Chrome(service='', options=chrome_options)
        print("Driver initialized successfully")
        return driver
    except Exception as e:
        print(f"Error initializing driver: {e}")
        return None  
