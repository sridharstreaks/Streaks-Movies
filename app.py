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
from web_utils import WebUtils
from movie_search_utils import MovieSearchUtils
from isaimini import Isaimini
from moviesda import MoviesDa
from movierulz import Movierulz
from tamilyogi import TamilYogi

# Create an instance of Different Domain class
isaimini = Isaimini()
moviesda = MoviesDa()
movierulz = Movierulz()
tamilyogi = TamilYogi()

# Initializing the WebUtils class
web_utils = WebUtils()

# Initialize the MovieSearchUtils class
movie_search = MovieSearchUtils()

domain_keyword_list=["isaimini","moviesda","movierulz","1tamilyogi"]

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

st.title("Streaks Movies - Direct Stream or Download Movies")

# Step 1: Text Input & Search Button
if st.session_state.step == 1:
    query = st.text_input("Enter a movie title", placeholder="Search your fav regional movies")
    if st.button("Search"):
        st.session_state.dictionary = {}  # Initialize an empty dictionary to store all results
        
        for domain_keyword in domain_keyword_list:
            if domain_keyword == "isaimini":
                results, url = isaimini.movie_search(query)
                st.session_state.dictionary.update(results)  # Merge results into the main dictionary
                st.session_state.url = url  # Save the URL (if needed for isaimini)

            elif domain_keyword == "moviesda":
                results = moviesda.movie_search(query)
                st.session_state.dictionary.update(results)

            elif domain_keyword == "movierulz":
                results = movierulz.movie_search(query)
                st.session_state.dictionary.update(results)

            elif domain_keyword == "1tamilyogi":
                results = tamilyogi.movie_search(query)
                st.session_state.dictionary.update(results)
        
        if st.session_state.dictionary:
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