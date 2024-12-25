import streamlit as st
import libtorrent as lt
import time
import os
import requests
from lxml import html

# Set up a directory for temporary storage
temp_dir = "temp_video"
os.makedirs(temp_dir, exist_ok=True)

# Initialize session state for libtorrent session and handle
if "torrent_session" not in st.session_state:
    st.session_state.torrent_session = lt.session()
    st.session_state.torrent_handle = None

# Function: get_domian
def domain_finder(previous_domain='.ru'):
    base_url="https://www.1tamilmv"
    response = requests.get(base_url+previous_domain)
    if response.status_code==200:
        tree = html.fromstring(response.content)
        current_domain=tree.xpath('//*[contains(text(),".") and @class]/text()')[0]
    current_url=base_url+current_domain
    return current_url  #redirection pending

# Function: movie_search
def movie_search(query,previous_domain='.ru'):
    dicto={}
    discard_words=['gdrive','Trailer','songs','drive']
    query=query.replace(" ","%20").lower()
    url=f"{domain_finder(previous_domain)}/index.php?/search/&q={query}&quick=1&search_and_or=and&search_in=titles&sortby=relevancy"
    response = requests.get(url)
    if response.status_code==200:
        tree = html.fromstring(response.content)
        range_inc=5
        for i in range(0,range_inc):
            try:
                if not any(dword.lower() in tree.xpath('//li[@data-role="activityItem"]//h2//a//text()')[i].lower() for dword in discard_words):
                    dicto[tree.xpath('//li[@data-role="activityItem"]//h2//a//text()')[i]] = tree.xpath('//li[@data-role="activityItem"]//h2//a//@href')[i]
                else:
                    range_inc+=1
            except IndexError:
                break
    return dicto

# Function: movie_quality
def movie_quality(link):
    dicto={}
    response = requests.get(link)
    if response.status_code==200:
        tree = html.fromstring(response.content)
    for i in range(0,int(tree.xpath('count(//a[@class="skyblue-button"]/@href)'))):
        try:
            dicto[tree.xpath('//a[@class="skyblue-button"]//preceding-sibling::strong[2]/text()')[i]]=tree.xpath('//a[@class="skyblue-button"]/@href')[i]
        except IndexError:
            break
    return dicto

# Function: movie_torrent
def start_download(magnet_link, save_path):
    """Start or resume downloading a torrent."""
    ses = st.session_state.torrent_session
    ses.apply_settings({'listen_interfaces': '0.0.0.0:6881,[::]:6881'})

    params = lt.add_torrent_params()
    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t(2)
    params.url = magnet_link

    handle = ses.add_torrent(params)
    st.session_state.torrent_handle = handle

    st.write("Downloading Metadata...")
    while not handle.status().has_metadata:
        time.sleep(1)
    st.write("Metadata Imported, Starting Download...")

# Monitor download progress with stqdm
def monitor_download():
    """Monitor download progress."""
    handle = st.session_state.torrent_handle
    if handle is None:
        st.warning("No active download session. Start a new download.")
        return

    progress_placeholder = st.empty()

    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        state_str = [
            "queued", "checking", "downloading metadata", "downloading", "finished",
            "seeding", "allocating", "checking fastresume"
        ]
        progress_info = (
            f"{s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s, "
            f"up: {s.upload_rate / 1000:.1f} kB/s, seeds: {s.num_seeds}, peers: {s.num_peers}) {state_str[s.state]}"
        )
        progress_placeholder.write(progress_info)
        time.sleep(5)

    st.success("Download Complete!")

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = 1
if "dictionary" not in st.session_state:
    st.session_state.dictionary = None
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "movie_quality" not in st.session_state:
    st.session_state.movie_quality = None

# Streamlit UI
st.title("Streaks Movies - Torrent Download Movies")

# Step 1: Movie Search
if st.session_state.step == 1:
    st.warning('Torrent speed depends on no. of seeds and peers', icon="⚠️")
    query = st.text_input("Enter movie name:", placeholder="Seach any of your fav movies")
    if st.button("Search"):
            st.session_state.dictionary = movie_search(query.strip())
            if st.session_state.dictionary:
                st.session_state.step = 2
                st.rerun()
            else:
                st.write("No results found")


# Step 2: Present Movie Options Based on Search
elif st.session_state.step == 2 and st.session_state.dictionary:
    st.warning('Please Select files within 1GB as this app\'s storage limit is max 1GB', icon="⚠️")
    selected_movie = st.pills("Select a movie:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Selection"):
        st.session_state.selected_movie = st.session_state.dictionary[selected_movie]
        st.session_state.step = 3
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'dictionary', 'selected_movie', 'movie_quality']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

# Step 3: Movie Quality
elif st.session_state.step == 3 and st.session_state.selected_movie:
    st.warning('Please Select files within 1GB as this app\'s storage limit is max 1GB', icon="⚠️")
    st.session_state.dictionary = movie_quality(st.session_state.selected_movie)
    movie_quality = st.pills("Select quality:", list(st.session_state.dictionary.keys()))
    if st.button("Confirm Quality"):
        st.session_state.movie_quality = st.session_state.dictionary[movie_quality]
        st.session_state.step = 4
        st.rerun()
    elif st.button("Start Over"):
        for key in ['step', 'dictionary', 'selected_movie', 'movie_quality']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

# Step 3: Torrent Download
elif st.session_state.step == 4 and st.session_state.movie_quality:
    st.warning('Please Select files within 1GB as this app\'s storage limit is max 1GB', icon="⚠️")
    if st.button("Start Download"):
        start_download(st.session_state.movie_quality, temp_dir)

        if st.session_state.torrent_handle:
            monitor_download()

    # Show download button if the file is completed
    if st.session_state.torrent_handle:
        handle = st.session_state.torrent_handle
        if handle.status().state == lt.torrent_status.seeding:
            completed_file_path = os.path.join(temp_dir, handle.status().name)
            if os.path.exists(completed_file_path):
                with open(completed_file_path, "rb") as f:
                    video_data = f.read()

                st.download_button(
                    label="Download Video",
                    data=video_data,
                    file_name=os.path.basename(completed_file_path),
                    mime="video/mp4"  # Adjust MIME type based on file type
                )

    if st.button("Start Over"):
        for key in ['step', 'dictionary', 'selected_movie', 'movie_quality']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()

    # Optional cleanup button to remove temporary files
    if st.button("Clear Temporary Files"):
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        st.success("Temporary files cleared.")