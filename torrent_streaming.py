import streamlit as st
import libtorrent as lt
import time
import os

# Set up a directory for temporary storage
temp_dir = "temp_video"
os.makedirs(temp_dir, exist_ok=True)

# Initialize session state for libtorrent session and handle
if "torrent_session" not in st.session_state:
    st.session_state.torrent_session = lt.session()
    st.session_state.torrent_handle = None

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

    while not os.path.exists(video_path) or not os.path.isfile(video_path):
        s = handle.status()
        st.write(
            f"Progress: {s.progress * 100:.2f}% (down: {s.download_rate / 1000:.1f} kB/s, "
            f"peers: {s.num_peers})"
        )
        time.sleep(5)

    # Check if sufficient pieces are downloaded for streaming
    piece_length = torrent_info.piece_length()
    downloaded_bytes = handle.status().total_done
    buffer_threshold = piece_length * 10  # Require at least 10 pieces for buffer

    if downloaded_bytes >= buffer_threshold:
        st.video(video_path)
    else:
        st.warning("Buffering... Please wait for more data to download.")

# Streamlit UI
st.title("Stream Torrent Video")

magnet_link = st.text_input("Enter Magnet Link:")
if magnet_link:
    if st.button("Start Stream"):
        st.write("Initializing stream...")
        start_torrent_stream(magnet_link, temp_dir)

if st.session_state.torrent_handle:
    if st.button("Stream Video"):
        monitor_and_stream_video()

# Optional cleanup button to remove temporary files
if st.button("Clear Temporary Files"):
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    st.success("Temporary files cleared.")