from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from web_utils import web_utils
from mongodb import MongoDBHandler
import streamlit as st


web_utils=web_utils()
# Initialize the MongoDB handler
db_handler = MongoDBHandler(st.secrets["connection_uri"])

class Tamilyogi():

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
    
    def movie_search(self,query):
        db_handler.connect_and_test() #makes connection with mongodb

        current_url = db_handler.get_current_url("tamilyogi") #gets the current url

        current_url=web_utils.get_url(current_url) #checks if current url is working

        url=db_handler.update_url_if_needed("tamilyogi",current_url) #captures any changes in the url domain

        if Tamilyogi.count_forward_slashes(current_url)>3:
            url=Tamilyogi.remove_extra_url(current_url) #ensure always returns the home page of the url.

        dicto = {}
        search_url = url + f"?s={query}"
        tree = web_utils.get_request(search_url)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath('count(//ul[@class="recent-posts"]//li)'))):
                dicto[tree.xpath('//ul[@class="recent-posts"]//li//h2//a/text()')[i]] = tree.xpath('//ul[@class="recent-posts"]//li//h2//a/@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto

    @staticmethod
    def quality_name_regex(url):
        # Regex to extract text after 'download/'
        match = re.search(r"download/(.+)", url)
        if match:
            extracted_text = match.group(1)
            return extracted_text
        else:
            return 'Unamed Quality'

    def movie_quality(self,selected_movie_link):
        dicto = {}
        # Save the response as an HTML file
        tree = web_utils.get_request(selected_movie_link)
        if tree is None:
            print("Error getting the webpage")
            return dicto
        try:
            for i in range(0, int(tree.xpath("count(//div[@class='entry-content']//span//a)"))):
                dicto[Tamilyogi.quality_name_regex(tree.xpath("//div[@class='entry-content']//span//a/@href")[i])] = tree.xpath("//div[@class='entry-content']//span//a/@href")[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed: {e}")
        return dicto
    
    @staticmethod
    def find_quality(url):
        checks=['720p','480p','240p']
        for check in checks:
            if check in url:
                return check
            else:
                continue
    
    def get_website_content(self,url):
        check=Tamilyogi.find_quality(url)
        driver = None
        try:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode (optional)
            chrome_options.add_argument('--disable-gpu')  # Disable GPU for headless mode
            chrome_options.add_argument('--window-size=1920,1200')  # Set Chrome window Size
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            # For local Development
            # service = Service('C:\\ChromeDriver_Path')  # Replace with your ChromeDriver path
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            time.sleep(5)
            #html_doc = driver.page_source
            if driver.find_elements(By.XPATH, '//span[contains(text(),"Download")]//a'):
                # Find all <a> tags whose href contains "droplare"
                element = driver.find_element(By.XPATH, f'//span[contains(text(),"Download")]//a[contains(@href,{check})]')
                element.click()
                time.sleep(5)
                #html_doc = driver.page_source
                if driver.find_element(By.XPATH, '//div[@id="dlWrapper"]//a'):
                # Find all <a> tags whose href contains "droplare"
                    elements = driver.find_elements(By.XPATH, '//div[@id="dlWrapper"]//a')

                # Extract the href attribute from each element
                hrefs = [element.get_attribute("href") for element in elements]
                if hrefs:
                    driver.quit()
                    return hrefs[0]
                else:
                    return None
            # logs = driver.get_log("performance")
            # driver.quit()
            # return logs
        except Exception as e:
            print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
        finally:
            if driver is not None:
                driver.quit()
        return None