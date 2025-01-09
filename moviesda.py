import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from web_utils import web_utils
from mongodb import MongoDBHandler
import streamlit as st


web_utils=web_utils()
# Initialize the MongoDB handler
db_handler = MongoDBHandler(st.secrets["connection_uri"])


class Moviesda():

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

        current_url = db_handler.get_current_url("moviesda") #gets the current url

        current_url=web_utils.get_url(current_url) #checks if current url is working

        url=db_handler.update_url_if_needed("moviesda",current_url) #captures any changes in the url domain

        if Moviesda.count_forward_slashes(current_url)>3:
            url=Moviesda.remove_extra_url(current_url) #ensure always returns the home page of the url.

        dicto = {}
        search_url = url + f"mobile/search?find={query.replace(' ', '+')}&per_page=1"
        tree = web_utils.get_request(search_url)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath("count(//div[@class='f']//a)"))):
                dicto[tree.xpath("//div[@class='f']//a/@title")[i]] = tree.xpath("//div[@class='f']//a/@href")[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto

    def movie_quality(self, selected_movie_link):
        dicto = {}
        tree = web_utils.get_request(selected_movie_link)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath("count(//ul[@class='sitelinks'])"))):
                dicto[tree.xpath("//ul[@class='sitelinks']//a//b/text()")[i]] = tree.xpath("//ul[@class='sitelinks']//a/@href")[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto

    def stream_link_fetcher(self, selected_quality):
        tree = web_utils.get_request(selected_quality)
        if tree is None:
            print("Error getting the webpage")
            return None
        try:
            if tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href"):
                return self.stream_link_fetcher(tree.xpath("//div[@class='f']//a[@class='dwnLink']/@href")[0])
            elif tree.xpath("//div[@class='downLink']//a[@class='dwnLink']/@href"):
                return selected_quality
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
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
            #html_doc = driver.page_source
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

    def extract_url_from_network_events(self, log):
        if log is not None:
            return log.get('params', {}).get('response', {}).get('url', None)
        else:
            return ""