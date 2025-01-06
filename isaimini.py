import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from web_utils import web_utils

web_utils=web_utils()

class Isaimini():

    @staticmethod
    def count_forward_slashes(url):
        return url.count('/')
    
    @staticmethod
    def remove_extra_url(url):
        # Find the index of the 3rd slash
        index = -1
        for i in range(3):
            index = url.find("/", index + 1)
            if index == -1:
                break

        # Remove everything after the 3rd slash
        if index != -1:
            result = url[:index + 1]
        else:
            result = url

        return result
    
    def movie_search(self, query):
        url = web_utils.domain_finder("isaimini")
        if Isaimini.count_forward_slashes(url)>3:
            url=Isaimini.remove_extra_url(url)
        dicto = {}
        search_url = url + f"mobile/search?find={query}&per_page=1"
        tree = web_utils.get_request(search_url)
        if tree is None:
            return dicto, url
        for i in range(0, int(tree.xpath('count(//div[@class="dir"]//a[contains(@href,{})]/text())'.format(url.replace("https://", "").replace("/", ""))))):
            dicto[tree.xpath('//div[@class="dir"]//a[contains(@href,{})]/text()'.format(url.replace("https://", "").replace("/", "")))[i]] = tree.xpath('//div[@class="dir"]//a[contains(@href,{})]/@href'.format(url.replace("https://", "").replace("/", "")))[i+1]
        return dicto, url

    def movie_quality(self, url, link):
        dicto = {}
        tree = web_utils.get_request(link)
        if tree is None:
            return dicto, url
        for i in range(0, int(tree.xpath('count(//div[@class="catList"]//a[contains(@href,{})])'.format(url.replace("https://", "").replace("/", ""))))):
            dicto[tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/text()'.format(url.replace("https://", "").replace("/", "")))[i * 2]] = tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/@href'.format(url.replace("https://", "").replace("/", "")))[i]
        return dicto, url

    def get_website_content(self, url):
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1200')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url.replace("file","view"))
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