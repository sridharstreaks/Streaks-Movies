import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
from web_utils import WebUtils


class Movierulz:
    def __init__(self):
        # Initialize reusable attributes if needed (e.g., headers for requests)
        self.web_utils = WebUtils()

    def movie_search(self, query):
        """
        Searches for a movie on the Movierulz website.
        """
        url = self.web_utils.domain_finder("movierulz")
        search_url = f"{url}search_movies?s={query}"
        tree = self.web_utils.get_request(search_url)
        if tree is None:
            return {}

        dicto = {}
        count = int(tree.xpath('count(//div[@class="content home_style"]//li)'))
        for i in range(count):
            movie_title = tree.xpath('//div[@class="content home_style"]//li//b/text()')[i]
            movie_link = tree.xpath('//div[@class="content home_style"]//li//@href')[i]
            dicto[movie_title] = movie_link
        return dicto

    def get_download_link(self, url):
        """
        Fetches the download link using Selenium.
        """
        driver = None
        try:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU
            chrome_options.add_argument("--window-size=1920,1200")  # Set Chrome window size
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )

            driver.get(url)
            time.sleep(5)  # Allow the page to load
            elements = driver.find_elements(By.XPATH, '//a[contains(@href,"droplare")]')
            hrefs = [element.get_attribute("href") for element in elements]
            driver.quit()
            return hrefs[0] if hrefs else None
        except Exception as e:
            print(f"DEBUG:GET_DOWNLOAD_LINK:ERROR:{e}")
        finally:
            if driver:
                driver.quit()
        return None

    def get_website_logs(self, url):
        """
        Fetches performance logs using Selenium after interacting with the website.
        """
        driver = None
        try:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU
            chrome_options.add_argument("--window-size=1920,1200")  # Set Chrome window size
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )

            driver.get(url)
            time.sleep(5)  # Allow the page to load

            # Simulate button click
            button = driver.find_element(By.ID, "downloadbtn")
            driver.execute_script("arguments[0].click();", button)

            logs = driver.get_log("performance")
            driver.quit()
            return logs
        except Exception as e:
            print(f"DEBUG:GET_WEBSITE_LOGS:ERROR:{e}")
        finally:
            if driver:
                driver.quit()
        return None

    def process_browser_logs_for_download_events(self, logs):
        """
        Processes browser logs to fetch relevant download events.
        """
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if log.get("method") == "Page.downloadWillBegin":
                return log
        return None

    def extract_url_from_download_event(self, log):
        """
        Extracts the download URL from the processed log entry.
        """
        return log.get("params", {}).get("url", None)