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

def monitor_download():
    """Monitor download progress."""
    handle = st.session_state.torrent_handle
    if handle is None:
        st.warning("No active download session. Start a new download.")
        return
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        state_str = [
            "queued", "checking", "downloading metadata", "downloading", "finished",
            "seeding", "allocating", "checking fastresume"
        ]
        progress_info = (
            f"{s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s, "
            f"up: {s.upload_rate / 1000:.1f} kB/s, peers: {s.num_peers}) {state_str[s.state]}"
        )
        st.write(progress_info)
        time.sleep(5)

    st.success("Download Complete!")

    # Streamlit UI
st.title("Torrent Video Downloader")

magnet_link = st.text_input("Enter Magnet Link:")
if magnet_link:
    if st.button("Start Download"):
        st.write("Starting download...")
        start_download(magnet_link, temp_dir)

if st.session_state.torrent_handle:
    if st.button("Monitor Progress"):
        monitor_download()

# Show download button if the file is completed
if st.session_state.torrent_handle:
    handle = st.session_state.torrent_handle
    if handle.status().state == lt.torrent_status.seeding:
        completed_file_path = os.path.join(temp_dir, handle.name())
        if os.path.exists(completed_file_path):
            with open(completed_file_path, "rb") as f:
                video_data = f.read()

            st.download_button(
                label="Download Video",
                data=video_data,
                file_name=os.path.basename(completed_file_path),
                mime="video/mp4"  # Adjust MIME type based on file type
            )

# Optional cleanup button to remove temporary files
if st.button("Clear Temporary Files"):
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    st.success("Temporary files cleared.")