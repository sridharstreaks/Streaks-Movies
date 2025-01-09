import streamlit as st
import libtorrent as lt
import time
import os

class Torrent_utils:
    def __init__(self, temp_dir="temp_video"):
        # Initialize attributes
        self.temp_dir = temp_dir
        self.ses = None
        self.handle = None
        self.streaming = False

        # Set up a directory for temporary storage
        os.makedirs(self.temp_dir, exist_ok=True)

        # Initialize the session state for the Streamlit app
        if "torrent_session" not in st.session_state:
            st.session_state.torrent_session = lt.session()
            st.session_state.torrent_handle = None
            st.session_state.streaming = False

    def start_torrent_stream(self, magnet_link, save_path):
        """Start streaming a torrent video."""
        ses = st.session_state.torrent_session
        # Apply torrent session settings
        ses.apply_settings({'listen_interfaces': '0.0.0.0:6881,[::]:6881'})

        # Prepare torrent parameters
        params = lt.add_torrent_params()
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t(2)
        params.url = magnet_link
        params.flags |= lt.torrent_flags.sequential_download  # Enable sequential download

        # Add torrent to session
        self.handle = ses.add_torrent(params)
        st.session_state.torrent_handle = self.handle
        st.write("Downloading Metadata...")

        # Wait for metadata to be fetched
        while not self.handle.status().has_metadata:
            time.sleep(1)

        # Set priorities for the first few pieces (e.g., first 25%)
        torrent_info = self.handle.torrent_file()
        for i in range(min(25, torrent_info.num_pieces())):
            self.handle.piece_priority(i, 7)  # 7 = highest priority
        st.write("Metadata Imported, Starting Stream...")

        st.session_state.streaming = True  # Set streaming flag to True

    def monitor_and_stream_video(self):
        """Monitor download progress and stream video."""
        if self.handle is None:
            st.warning("No active stream. Start a new session.")
            return

        # Get the torrent info and save path
        torrent_info = self.handle.torrent_file()
        video_path = os.path.join(self.temp_dir, torrent_info.files().file_path(0))  # Get the first file in the torrent
        buffer_placeholder = st.empty()  # Placeholder for buffering message
        progress_placeholder = st.empty()  # Placeholder for progress information
        video_placeholder = st.empty()  # Placeholder for video playback

        buffer_threshold = torrent_info.total_size() * (10/100)  # Require at least 10% for buffer
        buffer_ready = False

        while st.session_state.streaming:
            s = self.handle.status()
            downloaded_bytes = s.total_done

            if not buffer_ready:
                if downloaded_bytes < buffer_threshold:
                    buffer_placeholder.warning(f"Buffering... Please wait for {100 - round((downloaded_bytes/buffer_threshold)*100,2)}% more data to download.")
                else:
                    buffer_placeholder.empty()
                    buffer_ready = True
                    # Start video playback once buffer is ready
                    if os.path.exists(video_path) and os.path.isfile(video_path):
                        video_placeholder.video(video_path, autoplay=True)

            # Update progress
            progress_placeholder.write(
                f"Progress: {s.progress * 100:.2f}% (Down: {s.download_rate / 1000:.1f} kB/s, Up: {s.upload_rate / 1000:.1f} kB/s"
                f", Seeds: {s.num_seeds}, Peers: {s.num_peers})"
            )

            if s.progress >= 1:  # Check if download is complete
                st.success("Full video download completed.")
                st.session_state.streaming = False

                # Provide download option once download is complete
                if os.path.exists(video_path) and os.path.isfile(video_path):
                    with st.container():
                        st.write("Clicking on download will stop the video. Click Start Stream to play video Again")
                        st.download_button(
                            label="Download Video",
                            data=open(video_path, "rb").read(),
                            file_name=os.path.basename(video_path),
                        )
                
                break

            time.sleep(2)  # Reduce the polling frequency to avoid unnecessary reruns

    def reset_stream(self):
        """Reset and clean up resources."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))

        st.session_state.clear() 

        # Reset torrent session and clear session state
        st.session_state.torrent_session = lt.session()  # Re-initialize session
        st.session_state.torrent_handle = None
        st.session_state.streaming = False  # Stop the stream
        
        st.write("Temporary files cleared and torrent session reset.")
        st.session_state.step = 1
        st.rerun()  # Restart the Streamlit app