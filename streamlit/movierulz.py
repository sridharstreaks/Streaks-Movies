from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from web_utils import web_utils
from mongodb import MongoDBHandler
import streamlit as st


web_utils=web_utils()
# Initialize the MongoDB handler
db_handler = MongoDBHandler(st.secrets["connection_uri"])

class Movierulz():

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
        db_handler.connect_and_test() #makes connection with mongodb

        current_url = db_handler.get_current_url("movierulz") #gets the current url

        current_url=web_utils.get_url(current_url) #checks if current url is working

        url=db_handler.update_url_if_needed("movierulz",current_url) #captures any changes in the url domain

        if Movierulz.count_forward_slashes(current_url)>3:
            url=Movierulz.remove_extra_url(current_url) #ensure always returns the home page of the url.

        dicto = {}
        search_url = url + f"search_movies?s={query.replace(' ', '+')}"
        tree = web_utils.get_request(search_url)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath('count(//div[@class=\"content home_style\"]//li)'))):
                dicto[tree.xpath('//div[@class=\"content home_style\"]//li//b/text()')[i]] = tree.xpath('//div[@class=\"content home_style\"]//li//@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto
    
    def stream_link_fetcher(self, selected_movie_link):
        dicto = {}
        tree = web_utils.get_request(selected_movie_link)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath('count(//span[contains(text(), "Torrent")]/following::a[contains(@href, "magnet")]//small/text())'))):
                dicto[tree.xpath('//span[contains(text(), "Torrent")]/following::a[contains(@href, "magnet")]//small/text()')[i]] = tree.xpath('//span[contains(text(), "Torrent")]/following::a[contains(@href, "magnet")]/@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto

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

    def process_browser_logs_for_network_events(self,logs):
        if logs is not None:
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if log.get('method') == 'Page.downloadWillBegin':
                    return log
        else:
            return None

    def extract_url_from_network_events(self,log):
        if log is not None:
            return log.get('params', {}).get('url', None)
        else:
            return ""