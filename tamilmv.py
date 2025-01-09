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

class Tamilmv():

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

        current_url = db_handler.get_current_url("tamilmv") #gets the current url

        current_url=web_utils.get_url(current_url) #checks if current url is working

        url=db_handler.update_url_if_needed("tamilmv",current_url) #captures any changes in the url domain

        if Tamilmv.count_forward_slashes(current_url)>3:
            url=Tamilmv.remove_extra_url(current_url) #ensure always returns the home page of the url.

        dicto = {}
        search_url = url + f"index.php?/search/&q={query.replace(' ', '+')}&quick=1&search_and_or=or&search_in=titles&sortby=relevancy"
        tree = web_utils.get_request(search_url)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0,int(tree.xpath('count(//ol//h2[contains(@class,"StreamItem_title")]//a//text())'))):
                if not any(word in tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a//text()')[i] for word in ['OTT', 'Trailer']):
                    dicto[tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a//text()')[i]]=tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a/@href')[i]
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
            for i in range(0,int(tree.xpath('count(//a[@data-fileext="torrent"]//span/text())'))):
                dicto[tree.xpath('//a[@data-fileext="torrent"]//span/text()')[i]]=tree.xpath('//a[@class="skyblue-button"]/@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto

    # def movie_quality(self, selected_movie_link):
    #     dicto = {}
    #     tree = web_utils.get_request(selected_movie_link)
    #     if tree is None:
    #         print("Error getting the webpage")
    #         return dicto
    #     try:
    #         for i in range(0, int(tree.xpath('count(//div[@class="catList"]//a[contains(@href,{})])'.format(url.replace("https://", "").replace("/", ""))))):
    #             dicto[tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/text()'.format(url.replace("https://", "").replace("/", "")))[i * 2]] = tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/@href'.format(url.replace("https://", "").replace("/", "")))[i]
    #     except Exception as e:
    #         print(f"Error while Extracting the elements/ No proper Page formed: {e}")
    #     return dicto 

    # def get_website_logs(self, url):
    #     driver = None
    #     try:
    #         chrome_options = Options()
    #         chrome_options.add_argument('--headless')
    #         chrome_options.add_argument('--disable-gpu')
    #         chrome_options.add_argument('--window-size=1920,1200')
    #         chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    #         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #         driver.get(url.replace("file","view"))
    #         time.sleep(5)
    #         #html_doc = driver.page_source
    #         download_button = driver.find_element(By.XPATH, "//a[@class='dwnLink']")
    #         download_button.click()
    #         logs = driver.get_log("performance")
    #         driver.quit()
    #         return logs
    #     except Exception as e:
    #         print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    #     finally:
    #         if driver is not None:
    #             driver.quit()
    #     return None

    # def process_browser_logs_for_network_events(self, logs):
    #     if logs is not None:
    #         for entry in logs:
    #             log = json.loads(entry["message"])["message"]
    #             if log.get('method') == 'Network.responseReceived' and log.get('params', {}).get('response', {}).get('mimeType') == 'video/mp4':
    #                 return log
    #     else:
    #         return log

    # def extract_url_from_network_events(self, log):
    #     if log is not None: 
    #         return log.get('params', {}).get('response', {}).get('url', None)
    #     else:
    #         return ""