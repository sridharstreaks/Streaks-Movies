import streamlit as st
import time

from isaimini import Isaimini
from moviesda import Moviesda
from movierulz import Movierulz
from tamilyogi import Tamilyogi
from tamilblasters import Tamilblasters
from torrent_utils import Torrent_utils
from tamilmv import Tamilmv

isaimini=Isaimini()
moviesda=Moviesda()
movierulz=Movierulz()
tamilyogi=Tamilyogi()
tamilblasters=Tamilblasters()
tamilmv=Tamilmv()
torrent_utils=Torrent_utils()


######################################### Streamlit App #######################################################
# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = 1
if "url" not in st.session_state:
    st.session_state.url = None
if "query" not in st.session_state:
    st.session_state.query = None
if "dictionary" not in st.session_state:
    st.session_state.dictionary = None
if "selected_option_1" not in st.session_state:
    st.session_state.selected_option_1 = None
if "selected_option_2" not in st.session_state:
    st.session_state.selected_option_2 = None
if "streamlink" not in st.session_state:
    st.session_state.streamlink= None

direct_domain_keywords=['isaimini','moviesda','movierulz','1tamilyogi'] # Direct Download Domains
torrent_domain_keywords=['movierulz','tamilblasters','tamilmv']

# Streamlit app
st.title("Streaks Movies - Direct Stream or Download Movies")

# Step 1: Text Input & Search Button
if st.session_state.step == 1:
    st.session_state.query = st.text_input("Enter a movie title", placeholder="Seach your fav regional movies")
    if st.button("Search - Direct Stream/Download"):
        for each in direct_domain_keywords:
            #fetch resuts for isaimini
            if each == 'isaimini':
                result_dict, url = isaimini.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if result_dict:
                    # Add a prefix to all keys to avoid overwriting
                    result_dict = {f"server_1_{k}": v for k, v in result_dict.items()}
                    st.session_state.dictionary.update(result_dict)
                    st.session_state.url = url  # Update URL if applicable
            #fetch resuts for moviesda
            elif each == 'moviesda':
                results = moviesda.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"server_2_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)
            #fetch resuts for movierulz
            elif each == 'movierulz':
                results = movierulz.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"server_3_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)
            #fetch resuts for tamilyogi
            elif each == '1tamilyogi':
                results = tamilyogi.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"server_4_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)

        if st.session_state.dictionary and st.session_state.url:
            st.session_state.step = 2
            st.rerun()
        else:
            st.write("No results found")
            
#################################Fetching Torrent results############################
            
    elif st.button("Search - Torrent Stream/Download"):
        for each in torrent_domain_keywords:
            #fetch resuts for tamilyogi
            if each == 'tamilblasters':
                results = tamilblasters.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"torrent_server_1_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)
            if each == 'movierulz':
                results = movierulz.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"torrent_server_2_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)
            if each == 'tamilmv':
                results = tamilmv.movie_search(st.session_state.query)
                if st.session_state.dictionary is None:
                    st.session_state.dictionary = {}
                if results:
                    # Add a prefix to all keys to avoid overwriting
                    results = {f"torrent_server_2_{k}": v for k, v in results.items()}
                    st.session_state.dictionary.update(results)
        if st.session_state.dictionary and st.session_state.url:
            st.session_state.step = 6
            st.rerun()
        else:
            st.write("No results found")


# Step 2: Present Options Based on Search
elif st.session_state.step == 2 and st.session_state.dictionary and st.session_state.url:
    selected_option_1 = st.pills("Select an Movie option from Search Results:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Movie"):
        st.session_state.selected_option_1 = st.session_state.dictionary[selected_option_1]
        st.session_state.step = 3
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

# Step 3: Further Operations Based on Selection
elif st.session_state.step == 3 and st.session_state.selected_option_1:
    if "isaimini" in st.session_state.selected_option_1:
        st.session_state.dictionary,st.session_state.url = isaimini.movie_quality(st.session_state.url,st.session_state.selected_option_1)
        selected_option_2 = st.pills("Select an Movie option:", list(st.session_state.dictionary.keys()))
        if st.button("Confirm Movie Quality"):
            st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
            st.session_state.step = 4
            st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "moviesda" in st.session_state.selected_option_1:
        st.session_state.dictionary = moviesda.movie_quality(st.session_state.selected_option_1)
        selected_option_2 = st.pills("Select an Movie option:", list(st.session_state.dictionary.keys()))
        if st.button("Confirm Movie Quality"):
            st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
            st.session_state.step = 4
            st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "movierulz" in st.session_state.selected_option_1:
        if "streamlink" not in st.session_state or st.session_state.streamlink is None:
            with st.spinner("Fetching Streaming Link"):
                final_link = movierulz.get_website_content(st.session_state.selected_option_1)
                st.session_state.selected_option_2=final_link
                # Check if final_link is not None
                
                logs = movierulz.get_website_logs(final_link)
                if logs:
                    log = movierulz.process_browser_logs_for_network_events(logs)
                    st.session_state.streamlink = movierulz.extract_url_from_network_events(log)
                    st.success('Stream link fetched', icon="✅")
                else:
                    st.error("Download links not found. Try another versions")
        # Show the Play button only after the link is fetched  
        if st.session_state.streamlink:
            if st.button("Play"):
                st.session_state.step = 4
                st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "tamilyogi" in st.session_state.selected_option_1:
        st.session_state.dictionary = tamilyogi.movie_quality(st.session_state.selected_option_1)
        selected_option_2 = st.pills("Select an Movie option:", list(st.session_state.dictionary.keys()))
        if st.button("Confirm Movie Quality"):
            st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
            st.session_state.step = 4
            st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 4 and st.session_state.selected_option_2 and st.session_state.selected_option_1:
    if "isaimini" in st.session_state.selected_option_2:
        if "streamlink" not in st.session_state or st.session_state.streamlink is None:
            with st.spinner("Fetching Streaming Link"):
                #final_link,st.session_state.url = get_movie_link(st.session_state.url,st.session_state.selected_option_2)
        
                logs = isaimini.get_website_logs(st.session_state.selected_option_2)
        
                log = isaimini.process_browser_logs_for_network_events(logs)
        
                st.session_state.streamlink = isaimini.extract_url_from_network_events(log)
                st.success('stream link fetched', icon="✅")
        # Show the Play button only after the link is fetched  
        if st.session_state.streamlink:
            if st.button("Play"):
                st.session_state.step = 5
                st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "moviesda" in st.session_state.selected_option_2:
        if "streamlink" not in st.session_state or st.session_state.streamlink is None:
            with st.spinner("Fetching Streaming Link"):
                final_link = moviesda.stream_link_fetcher(st.session_state.selected_option_2)
        
                logs = moviesda.get_website_logs(final_link)
        
                log = moviesda.process_browser_logs_for_network_events(logs)
        
                st.session_state.streamlink = moviesda.extract_url_from_network_events(log)
                st.success('stream link fetched', icon="✅")
        # Show the Play button only after the link is fetched  
        if st.session_state.streamlink:
            if st.button("Play"):
                st.session_state.step = 5
                st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "droplare" in st.session_state.selected_option_2:
        st.video(st.session_state.streamlink,autoplay=True)
        time.sleep(5)
        st.link_button("Save to Device",st.session_state.streamlink,type="primary")

        #Start Over button
        if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "rajtamil" in st.session_state.selected_option_2:
        if "streamlink" not in st.session_state or st.session_state.streamlink is None:
            with st.spinner("Fetching Streaming Link"):
                st.session_state.streamlink = tamilyogi.get_website_content(st.session_state.selected_option_1)

                st.success('stream link fetched', icon="✅")
        # Show the Play button only after the link is fetched  
        if st.session_state.streamlink:
            if st.button("Play"):
                st.session_state.step = 5
                st.rerun()
        if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
elif st.session_state.step == 5:
    if "isaimini" in st.session_state.selected_option_2:
        st.video(st.session_state.streamlink,autoplay=True)
        time.sleep(5)
        st.link_button("Save to Device",st.session_state.streamlink,type="primary")

        #Start Over button
        if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "moviesda" in st.session_state.selected_option_2:
        st.video(st.session_state.streamlink,autoplay=True)
        time.sleep(5)
        st.link_button("Save to Device",st.session_state.streamlink,type="primary")

        #Start Over button
        if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    elif "rajtamil" in st.session_state.selected_option_2:
        st.video(st.session_state.streamlink,autoplay=True)
        time.sleep(5)
        st.link_button("Save to Device",st.session_state.streamlink,type="primary")

        #Start Over button
        if st.button("**Wanna watch/download another Movie?**",icon="🚨"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()

#################################################Torrents Sections############################################################

# Step 2: Present Options Based on Search
elif st.session_state.step == 6 and st.session_state.dictionary:
    selected_option_1 = st.pills("Select an Movie option from Search Results:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Movie"):
        st.session_state.selected_option_1 = st.session_state.dictionary[selected_option_1]
        st.session_state.step = 7
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

# Step 3: Further Operations Based on Selection
elif st.session_state.step == 7 and st.session_state.selected_option_1:
    if "tamilblasters" in st.session_state.selected_option_1:
        if "streamlink" not in st.session_state or st.session_state.streamlink is None:
            st.session_state.streamlink = tamilblasters.stream_link_fetcher(st.session_state.selected_option_1)
            if st.session_state.streamlink:
                st.write("Initializing stream...")
                torrent_utils.start_torrent_stream(st.session_state.streamlink, torrent_utils.temp_dir)
            if st.session_state.streaming:
                torrent_utils.monitor_and_stream_video()

                # Optional cleanup button to remove temporary files
                if st.button("Reset"):
                    torrent_utils.reset_stream()

    if "movierulz" in st.session_state.selected_option_1:
        st.session_state.dictionary = movierulz.stream_link_fetcher(st.session_state.selected_option_1)
        selected_option_2 = st.pills("Select the Movie Quality:", list(st.session_state.dictionary.keys()))
        if st.button("Confirm Movie Quality"):
            st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
            st.session_state.step = 8
            st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()
    
    if "tamilmv" in st.session_state.selected_option_1:
        st.session_state.dictionary = tamilmv.movie_quality(st.session_state.selected_option_1)
        selected_option_2 = st.pills("Select the Movie Quality:", list(st.session_state.dictionary.keys()))
        if st.button("Confirm Movie Quality"):
            st.session_state.selected_option_2 = st.session_state.dictionary[selected_option_2]
            st.session_state.step = 8
            st.rerun()
        elif st.button("Start Over"):
            for key in ['step', 'url', 'query', 'selected_option_1', 'selected_option_2','streamlink']:
                st.session_state[key] = None
            st.session_state.step = 1
            st.rerun()

# Step 3: Further Operations Based on Selection
elif st.session_state.step == 8 and st.session_state.selected_option_2:
    if "streamlink" not in st.session_state or st.session_state.streamlink is None:
        st.session_state.streamlink = st.session_state.selected_option_2
        if st.session_state.streamlink:
            st.write("Initializing stream...")
            torrent_utils.start_torrent_stream(st.session_state.streamlink, torrent_utils.temp_dir)
        if st.session_state.streaming:
            torrent_utils.monitor_and_stream_video()

            # Optional cleanup button to remove temporary files
            if st.button("Reset"):
                torrent_utils.reset_stream()