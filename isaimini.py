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


class Isaimini:
    def __init__(self):
        # Initialize reusable attributes if needed (e.g., headers for requests)
       self.web_utils = WebUtils()

    def movie_search(self, query):
        """
        Searches for a movie on the Isaimini website.
        """
        url = self.web_utils.domain_finder("isaimini")
        if not url:
            return {}, None

        dicto = {}
        search_url = url + f"mobile/search?find={query}&per_page=1"
        tree = self.web_utils.get_request(search_url)
        if tree:
            count = int(
                tree.xpath(
                    f'count(//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/text())'
                )
            )
            for i in range(count):
                movie_name = tree.xpath(
                    f'//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/text()'
                )[i]
                movie_link = tree.xpath(
                    f'//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/@href'
                )[i + 1]
                dicto[movie_name] = movie_link
        return dicto, url

    def movie_quality(self, url, link):
        """
        Fetches available quality options for a movie.
        """
        dicto = {}
        tree = self.web_utils.get_request(link)
        if tree:
            count = int(
                tree.xpath(
                    f'count(//div[@class="catList"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")])'
                )
            )
            for i in range(count):
                quality_name = tree.xpath(
                    f'//div[@class="catList"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/text()'
                )[i * 2]
                quality_link = tree.xpath(
                    f'//div[@class="catList"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/@href'
                )[i]
                dicto[quality_name] = quality_link
        return dicto

    def get_website_content(self, url):
        """
        Uses Selenium to interact with a website and fetch logs after clicking a download button.
        """
        driver = None
        try:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU
            chrome_options.add_argument("--window-size=1920,1200")
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )
            driver.get(url)
            time.sleep(5)  # Allow the page to load
            download_button = driver.find_element(
                By.XPATH, "//a[@class='dwnLink']"
            )  # Adjust XPath if necessary
            download_button.click()

            logs = driver.get_log("performance")
            driver.quit()
            return logs
        except Exception as e:
            print(f"DEBUG:GET_WEBSITE_CONTENT:ERROR:{e}")
        finally:
            if driver:
                driver.quit()
        return None

    def process_browser_logs_for_network_events(self, logs):
        """
        Processes browser logs to fetch relevant network events.
        """
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if (
                log.get("method") == "Network.responseReceived"
                and log.get("params", {}).get("response", {}).get("mimeType") == "video/mp4"
            ):
                return log
        return None

    def extract_url(self, log):
        """
        Extracts a URL from the processed log entry.
        """
        return log.get("params", {}).get("response", {}).get("url", None)