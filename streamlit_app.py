import streamlit as st

Movies_v1 = st.Page("regional_movies_v1.py", title="Stream or Download Regional Movies V1")
Movies_v2 = st.Page("regional_movies_v2.py", title="Stream or Download Regional Movies V2")
Torrent_Movies_Download = st.Page("torrent_download.py", title="Download Movie Torrents")
Torrent_Movies_Streaming = st.Page("torrent_streaming.py", title="Stream Movie Torrents")

pg = st.navigation([Movies_v1, Movies_v2, Torrent_Movies_Download, Torrent_Movies_Streaming])
st.set_page_config(page_title="Streaks Movies - Stream or download your Favorite movies", page_icon=":movie_camera:")
pg.run()