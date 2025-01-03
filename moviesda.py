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

class MoviesDa:
    def __init__(self):
        # Initialize reusable attributes if needed (e.g., headers for requests)
        self.web_utils = WebUtils()

    def movie_search(self, query):
        """
        Searches for a movie on the MoviesDa website.
        """
        url = self.web_utils.domain_finder("moviesda")
        if not url:
            return {}, None
        dicto = {}
        search_url = url + f"mobile/search?find={query.replace(' ', '+')}&per_page=1"
        tree = self.web_utils.get_request(search_url)
        count = int(tree.xpath("count(//div[@class='f']//a)"))
        for i in range(count):
            movie_title = tree.xpath("//div[@class='f']//a/@title")[i]
            movie_link = tree.xpath("//div[@class='f']//a/@href")[i]
            dicto[movie_title] = movie_link
        return dicto

    def movie_quality(self, selected_movie_link):
        """
        Fetches available quality options for a selected movie.
        """
        if selected_movie_link.strip():
            dicto = {}
            tree = self.web_utils.get_request(selected_movie_link)
            count = int(tree.xpath("count(//ul[@class='sitelinks'])"))
            for i in range(count):
                quality_name = tree.xpath("//ul[@class='sitelinks']//a//b/text()")[i]
                quality_link = tree.xpath("//ul[@class='sitelinks']//a/@href")[i]
                dicto[quality_name] = quality_link
            return dicto
        return {}

    def stream_link_fetcher(self, selected_quality):
        """
        Fetches the direct stream link for a selected quality.
        """
        url = selected_quality
        tree = self.web_utils.get_request(url)
        if tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href"):
            return self.stream_link_fetcher(tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href")[0])
        elif tree.xpath("//div[@class='downLink']//a[@class='dwnLink']/@href"):
            return url

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
