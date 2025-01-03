import time
import re
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from web_utils import WebUtils

class TamilYogi:
    def __init__(self):
        self.web_utils = WebUtils()

    def movie_search(self, query):
        """
        Searches for a movie on the 1TamilYogi website.
        """
        url = self.web_utils.domain_finder("1tamilyogi")
        search_url = f"{url}?s={query}"
        tree = self.web_utils.get_request(search_url)
        if tree is None:
            return {}

        dicto = {}
        count = int(tree.xpath('count(//ul[@class="recent-posts"]//li)'))
        for i in range(count):
            movie_title = tree.xpath('//ul[@class="recent-posts"]//li//h2//a/text()')[i]
            movie_link = tree.xpath('//ul[@class="recent-posts"]//li//h2//a/@href')[i]
            dicto[movie_title] = movie_link
        return dicto

    def quality_name_regex(self, url):
        """
        Extracts the quality name from a URL using regex.
        """
        match = re.search(r"download/(.+)", url)
        return match.group(1) if match else "Unnamed Quality"

    def movie_quality(self, selected_movie_link):
        """
        Fetches the available qualities and their respective download links for a selected movie.
        """
        if not selected_movie_link.strip():
            return {}

        response = requests.get(selected_movie_link, headers=self.headers)
        if response.status_code != 200:
            return {}

        tree = html.fromstring(response.content)
        dicto = {}
        count = int(tree.xpath('count(//div[@class="entry-content"]//span//a)'))
        for i in range(count):
            quality_name = self.quality_name_regex(
                tree.xpath("//div[@class='entry-content']//span//a/@href")[i]
            )
            download_link = tree.xpath("//div[@class='entry-content']//span//a/@href")[i]
            dicto[quality_name] = download_link
        return dicto

    def stream_link_fetcher(self, url):
        """
        Fetches the stream link using Selenium.
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
            elements = driver.find_elements(By.XPATH, '//div[@id="dlWrapper"]//a')
            hrefs = [element.get_attribute("href") for element in elements]
            driver.quit()
            return hrefs[0] if hrefs else None
        except Exception as e:
            print(f"DEBUG:STREAM_LINK_FETCHER:ERROR:{e}")
        finally:
            if driver:
                driver.quit()
        return None
