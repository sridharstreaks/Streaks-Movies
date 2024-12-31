import streamlit as st
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time  # To allow time for JavaScript to execute
import requests
import json
import requests
from lxml import html

payload = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
'Accept-Language': 'da, en-gb, en',
'Accept-Encoding': 'gzip, deflate, br',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Referer': 'https://www.google.com/'
}

############################################### Functions used to fetch inital links ####################################################

def get_request(url): #to get html request for a website
    response = requests.get(url)
    if response.status_code==200:
        tree = html.fromstring(response.content)
        return tree

def domain_finder(domain_keyword):
     # get the working website ignoring the faulty ones
    url=f'https://www.google.com/search?q={domain_keyword.replace(" ", "+")}'
    response = requests.get(url,headers=payload)
    tree = html.fromstring(response.content)
    links= tree.xpath('//h3/parent::a/@href')
    for each in links:
        tree=get_request(each)
        if tree.xpath('//form') != []:
            return each
        else:
            continue

def movie_search(query):
    url=domain_finder("isaimini")
    #print(url)
    dicto={}
    search_url=url+f"mobile/search?find={query}&per_page=1"
    tree=get_request(search_url)
    for i in range(0,int(tree.xpath('count(//div[@class="dir"]//a[contains(@href,{})]/text())'.format(url.replace("https://","").replace("/",""))))):
        #print(int(tree.xpath(f'count(//div[@class="dir"]//a[contains(@href,"https://www.isaimini.business.in/")]/text())')))
        dicto[tree.xpath('//div[@class="dir"]//a[contains(@href,{})]/text()'.format(url.replace("https://","").replace("/","")))[i]]=tree.xpath('//div[@class="dir"]//a[contains(@href,{})]/@href'.format(url.replace("https://","").replace("/","")))[i+1]
    return dicto,url

def movie_quality(url,link):
    dicto={}
    tree=get_request(link)
    for i in range(0,int(tree.xpath('count(//div[@class="catList"]//a[contains(@href,{})])'.format(url.replace("https://","").replace("/",""))))):
        #print(int(tree.xpath(f'count(//div[@class="dir"]//a[contains(@href,"https://www.isaimini.business.in/")]/text())')))
        dicto[tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/text()'.format(url.replace("https://","").replace("/","")))[i*2]]=tree.xpath('//div[@class="catList"]//a[contains(@href,{})]/@href'.format(url.replace("https://","").replace("/","")))[i]
    return dicto,url

#    def get_movie_link(url,link):
#        base_url=url
#        tree = html.fromstring(get_website_content(link))
#        links = tree.xpath('//a[@class="dwnLink" and contains(@href, {})]/@href'.format(url.replace("https://","").replace("/","")))
#        print(links)
#        if not links:  # If no links are found, return None or an appropriate value
#            return link, base_url
#        
#        while links:
#            next_url = links[0]
#            return get_movie_link(base_url,next_url)  # Pass the first URL to the recursive function
#        
#        return next_url,url

######################################## End of Initial Links Extraction ##########################################################

######################################### Stream Link Extraction #######################################################

def get_website_content(url): #uses selenium to mimic a click
    driver = None
    try:
        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode (optional)
        chrome_options.add_argument('--disable-gpu')  # Disable GPU for headless mode
        chrome_options.add_argument('--window-size=1920,1200') # Set Chrome window Size
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # For local Development                          
        #service = Service('C:\\ChromeDriver_Path')  # Replace with your ChromeDriver path
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        #st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        time.sleep(5)
        html_doc = driver.page_source
        download_button = driver.find_element(By.XPATH, "//a[@class='dwnLink']")  # Adjust XPath to match your case
        download_button.click()
        logs = driver.get_log("performance")
        driver.quit()
        return logs
    except Exception as e:
        print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
            if driver is not None: driver.quit()
    return None


def process_browser_logs_for_network_events(logs): #process and fetch only relevant log file
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if log.get('method') == 'Network.responseReceived' and log.get('params', {}).get('response', {}).get('mimeType') == 'video/mp4':
            #st.write(type(log)) for debugging
            return log
        
#extract the streamlink from logs
def extract_url(log):
    # Safely navigate the nested dictionary to get the 'url' value
    return log.get('params', {}).get('response', {}).get('url', None)

######################################### Stream Link Extraction Ends #######################################################
# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = 1
if "url" not in st.session_state:
    st.session_state.url = None
if "dictionary" not in st.session_state:
    st.session_state.dictionary = None
if "selected_option_1" not in st.session_state:
    st.session_state.selected_option_1 = None
if "selected_option_2" not in st.session_state:
    st.session_state.selected_option_2 = None
if "streamlink" not in st.session_state:
    st.session_state.streamlink= None

# Streamlit app
st.title("Streaks Movies - Direct Stream or Download Movies V1")
st.caption("Movies in this version is available in 480p and 720p.")


# Step 1: Text Input & Search Button
if st.session_state.step == 1:
    query = st.text_input("Enter a movie title", placeholder="Seach your fav regional movies")
    if st.button("Search"):
        st.session_state.dictionary,st.session_state.url = movie_search(query)
        if st.session_state.dictionary and st.session_state.url:
            st.session_state.step = 2
            st.rerun()
        else:
            st.write("No results found")

# Step 2: Present Options Based on Search
elif st.session_state.step == 2 and st.session_state.dictionary and st.session_state.url:
    selected_option_1 = st.pills("Select an Movie option:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Movie"):
        st.session_state.selected_option_1 = st.session_state.dictionary[selected_option_1]
        st.session_state.step = 3
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'search_result', 'first_selection', 'second_result', 'final_selection']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

# Step 3: Further Operations Based on Selection
elif st.session_state.step == 3 and st.session_state.selected_option_1:
    st.session_state.dictionary,st.session_state.url = movie_quality(st.session_state.url,st.session_state.selected_option_1)
    selected_option_2 = st.pills("Select an Movie option:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Movie Quality"):
        st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
        st.session_state.step = 4
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'search_result', 'first_selection', 'second_result', 'final_selection']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 4 and st.session_state.selected_option_2:
    if "streamlink" not in st.session_state or st.session_state.streamlink is None:
        with st.spinner("Fetching Streaming Link"):
            #final_link,st.session_state.url = get_movie_link(st.session_state.url,st.session_state.selected_option_2)
    
            logs = get_website_content(st.session_state.selected_option_2.replace("file","view"))
    
            log = process_browser_logs_for_network_events(logs)
    
            st.session_state.streamlink = extract_url(log)
            st.success('stream link fetched', icon="✅")
    # Show the Play button only after the link is fetched  
    if st.session_state.streamlink:
        if st.button("Play"):
            st.session_state.step = 5
            st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'search_result', 'first_selection', 'second_result', 'final_selection']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 5:
    st.video(st.session_state.streamlink,autoplay=True)
    time.sleep(5)
    st.link_button("Save to Device",st.session_state.streamlink,type="primary")

    #Start Over button
    if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
        for key in ['step', 'dictionary', 'selected_option_1', 'selected_option_2', 'streamlink']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()