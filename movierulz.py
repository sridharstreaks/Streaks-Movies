from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from lxml import html
from web_utils import web_utils

web_utils=web_utils()

class Movierulz():
    def movie_search(self, query):
        url = web_utils.domain_finder("movierulz")
        dicto = {}
        search_url = url + f"search_movies?s={query}"
        tree = web_utils.get_request(search_url)
        for i in range(0, int(tree.xpath('count(//div[@class=\"content home_style\"]//li)'))):
            dicto[tree.xpath('//div[@class=\"content home_style\"]//li//b/text()')[i]] = tree.xpath('//div[@class=\"content home_style\"]//li//@href')[i]
        return dicto

    def get_download_link(self, url):
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

            elements = driver.find_elements(By.XPATH, '//a[contains(@href,"droplare")]')
            hrefs = [element.get_attribute("href") for element in elements]
            driver.quit()
            return hrefs[0] if hrefs else None
        except Exception as e:
            print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
        finally:
            if driver is not None:
                driver.quit()
        return None

    def get_website_logs(self, url):
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

            button = driver.find_element(By.ID, "downloadbtn")
            driver.execute_script("arguments[0].click();", button)

            logs = driver.get_log("performance")
            driver.quit()
            return logs
        except Exception as e:
            print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
            return None
        finally:
            if driver is not None:
                driver.quit()

    def process_browser_logs_for_download_events(self,logs):
        if logs is not None:
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if log.get('method') == 'Page.downloadWillBegin':
                    return log
        else:
            return None

    def extract_url_from_download_event(self,log):
        if log is not None:
            return log.get('params', {}).get('url', None)
        else:
            return ""