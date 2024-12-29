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
def domain_finder():
    base_url="https://hacker9.com/tamilmv-proxy-list-of-1tamilmv-proxy-sites/"
    response = requests.get(base_url)
    if response.status_code==200:
        tree = html.fromstring(response.content)
        current_domain=tree.xpath('//table//td[@class="site"]//a/@href')[0]
    return current_domain  #redirection pending

# Function: movie_search
def movie_search(query):
    dicto={}
    discard_words=['gdrive','Trailer','songs','drive']
    query=query.replace(" ","%20").lower()
    url=f"{domain_finder()}index.php?/search/&q={query}&quick=1&search_and_or=and&search_in=titles&sortby=relevancy"
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

def start_torrent_stream(magnet_link, save_path):
    """Start streaming a torrent video."""
    ses = st.session_state.torrent_session
    ses.apply_settings({'listen_interfaces': '0.0.0.0:6881,[::]:6881'})

    params = lt.add_torrent_params()
    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t(2)
    params.url = magnet_link
    params.flags |= lt.torrent_flags.sequential_download  # Enable sequential download

    handle = ses.add_torrent(params)
    st.session_state.torrent_handle = handle

    st.write("Downloading Metadata...")
    while not handle.has_metadata():
        time.sleep(1)
    st.write("Metadata Imported, Starting Stream...")

    # Set priorities for the first few pieces (e.g., first 10%)
    torrent_info = handle.torrent_file()
    for i in range(min(10, torrent_info.num_pieces())):
        handle.piece_priority(i, 7)  # 7 = highest priority

def monitor_and_stream_video():
    """Monitor download progress and stream video."""
    handle = st.session_state.torrent_handle
    if handle is None:
        st.warning("No active stream. Start a new session.")
        return

    # Get the torrent info and save path
    torrent_info = handle.torrent_file()
    video_path = os.path.join(temp_dir, torrent_info.files().file_path(0))  # Get the first file in the torrent

    progress_placeholder = st.empty()
    video_placeholder = st.empty()

    while True:
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

        # Check if sufficient pieces are downloaded for streaming
        piece_length = torrent_info.piece_length()
        downloaded_bytes = handle.status().total_done
        buffer_threshold = piece_length * 3  # Require at least 3 pieces for buffer

        if os.path.exists(video_path) and os.path.isfile(video_path) and downloaded_bytes > buffer_threshold:
            video_placeholder.video(video_path)
            break
        else:
            st.warning("Buffering... Please wait for more data to download.")

        time.sleep(5)

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
st.title("Stream Torrent Video")

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
    if st.button("Start Streaming"):
        st.write("Initializing stream...")
        start_torrent_stream(st.session_state.movie_quality, temp_dir)

        if st.session_state.torrent_handle:
                monitor_and_stream_video()

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