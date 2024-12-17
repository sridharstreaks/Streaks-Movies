import requests
from lxml import html
import time
import random
import streamlit as st
import re

payload = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
'Accept-Language': 'da, en-gb, en',
'Accept-Encoding': 'gzip, deflate, br',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Referer': 'https://www.google.com/'
}

def strip_domain_pattern(movie_url):
    pattern = r"(?<=url\?q=)(https[^&]+)(?=&)"
    match = re.search(pattern, movie_url)
    return match.group(1)

def get_domian(search_keyword,as_sitesearch=None):
    dicto={}
    if as_sitesearch is None:
        url=f'https://www.google.com/search?q={search_keyword.replace(" ", "+")}'
        response = requests.get(url, headers= payload)
        if response.status_code==200:
            tree = html.fromstring(response.content)
            domain_name=str(tree.xpath('//div[@class="yuRUbf"]//a[@href and not(@disabled)]/@href')[0]).replace("https://", "").replace("/", "")
        return domain_name
    else:
        url=f'https://www.google.com/search?q={search_keyword.replace(" ", "+").lower()}&as_sitesearch={as_sitesearch}'
        response = requests.get(url)
        if response.status_code==200:
            # Save the response as an HTML file
            tree = html.fromstring(response.content)
            try:
                movie_url=str(tree.xpath(f'//a[contains(@href,{search_keyword.replace(" ","-").lower()}) and contains(@href,"movies") and contains(@href,"movie-download") and not(contains(@href,"google"))]/@href')[0])
                if "url?q" in movie_url:
                    movie_url=strip_domain_pattern(movie_url)
                else:
                    pass
            except IndexError:
                movie_url=str(tree.xpath('//a[contains(@href,"movie/page") and contains(@href,"movies") and not(contains(@href,"google"))]/@href')[0])
                if "url?q" in movie_url:
                    movie_url=strip_domain_pattern(movie_url)
                else:
                    pass
            print(movie_url)
            dicto[search_keyword]=movie_url
        return dicto

def download_link_fetcher(dicto):
    while not any(".dl" in value or ".mp4" in value for value in dicto.values()):
        print(".mp4 not found. Continuing the loop.")
        if len(dicto) > 0:
            *_, last = dicto.values()
        print(last)
        response = requests.get(last)
        tree = html.fromstring(response.content)
        if tree.xpath('count(//div[@class="f"])') > 0 and tree.xpath('count(//div[@class="bf"]//div[@class="f"])') == 0:
            try:
                dicto[tree.xpath('//div[@class="f"]//a//font[not(contains(text(),"Sample"))]/text()')[0]] = "https://3moviesda.com"+tree.xpath('//div[@class="f"]//a//font[not(contains(text(),"Sample"))]//parent::a/@href')[0]
            except IndexError:
                dicto[tree.xpath('//div[@class="f"]//a[not(contains(text(),"Sample"))]/text()')[0]] = "https://3moviesda.com"+tree.xpath('//div[@class="f"]//a[not(contains(text(),"Sample"))]//parent::a/@href')[0]
        elif tree.xpath('count(//div[@class="dlink"]//a[not(contains(@rel,"norefferrer"))])') > 0:
            dicto[tree.xpath('//div[@class="dlink"]//a/text()')[0]] = tree.xpath('//div[@class="dlink"]//a/text()//parent::a/@href')[0]
        elif tree.xpath('count(//div[@class="dlink"]//a[contains(@rel,"norefferrer")])') > 0:
            dicto[tree.xpath('//div[@class="dlink"]//a/text()')[0]] = tree.xpath('//div[@class="dlink"]//a/text()//parent::a/@href')[0]
        else:
            print("Movie Not Found")
            break
        time.sleep(random.randint(0,5))
    return dicto

def get_streamlink(dicto):
    *_, last = dicto.values()
    if ".dl" in last:
        last=last+"?dl=1"
    return last

st.set_page_config(
    page_title="Streaks Movies - Your New Movie Experience",
    page_icon=":movie_camera:",  # Favicon emoji
    layout="centered",  # Page layout option
)

# Streamlit app
st.title("Streaks Movies - Stream or Download Movies")

# Text input for user
input_text = st.text_input("Enter your text below:", placeholder="Type here and press Enter...")

if st.button('Search'):
    # Trigger first function
    get_domian_result = get_domian(input_text,"3moviesda.com")

    with st.spinner('Fetching Stream Link'):
        # Trigger second function with the result of the first
        download_link_fetcher_result = download_link_fetcher(get_domian_result)
        st.success('Download link fetched', icon="✅")

    # Final streaming link extractor
    video_path = get_streamlink(download_link_fetcher_result)

    if ".mp4" or "?dl=1" in video_path:
        # Display the video if the file exists
        try:
            st.video(video_path)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    time.sleep(5)

    st.markdown("High loading times? Directly download the file instead using the link below")
    time.sleep(2)
    st.markdown(":rainbow[Click here to Download!!!]")
    time.sleep(1)
    st.link_button("Direct Download",video_path,type="primary",icon="⬇️")
