import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
from web_utils import web_utils

web_utils=web_utils()

class Moviesda():
    def movie_search(self, query):
        url = web_utils.domain_finder("moviesda")
        dicto = {}
        search_url = url + f"mobile/search?find={query.replace(' ', '+')}&per_page=1"
        tree = web_utils.get_request(search_url)
        if tree is None:
            return dicto
        for i in range(0, int(tree.xpath("count(//div[@class='f']//a)"))):
            dicto[tree.xpath("//div[@class='f']//a/@title")[i]] = tree.xpath("//div[@class='f']//a/@href")[i]
        return dicto

    def movie_quality(self, selected_movie_link):
        dicto = {}
        tree = web_utils.get_request(selected_movie_link)
        if tree is None:
            return dicto
        for i in range(0, int(tree.xpath("count(//ul[@class='sitelinks'])"))):
            dicto[tree.xpath("//ul[@class='sitelinks']//a//b/text()")[i]] = tree.xpath("//ul[@class='sitelinks']//a/@href")[i]
        return dicto

    def stream_link_fetcher(self, selected_quality):
        tree = web_utils.get_request(selected_quality)
        if tree is None:
            return None
        if tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href"):
            return self.stream_link_fetcher(tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href")[0])
        elif tree.xpath("//div[@class='downLink']//a[@class='dwnLink']/@href"):
            return selected_quality

    def get_website_content(self, url):
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1200')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            time.sleep(5)
            html_doc = driver.page_source
            download_button = driver.find_element(By.XPATH, "//a[@class='dwnLink']")
            download_button.click()
            logs = driver.get_log("performance")
            driver.quit()
            return logs
        except Exception as e:
            print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
        finally:
            if driver is not None:
                driver.quit()
        return None

    def process_browser_logs_for_network_events(self, logs):
        if logs is not None:
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if log.get('method') == 'Network.responseReceived' and log.get('params', {}).get('response', {}).get('mimeType') == 'video/mp4':
                    return log
        else:
            return log

    def extract_url(self, log):
        if log is not None:
            return log.get('params', {}).get('response', {}).get('url', None)
        else:
            return ""