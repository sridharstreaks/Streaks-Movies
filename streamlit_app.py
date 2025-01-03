import streamlit as st

Movies_d1 = st.Page("regional_movies_d1.py", title="Stream or Download Regional Movies Domain 1")
Movies_d2 = st.Page("regional_movies_d2.py", title="Stream or Download Regional Movies Domain 2")
Movies_d3 = st.Page("regional_movies_d3.py", title="Stream or Download Regional Movies Domain 3")
Movies_d4 = st.Page("regional_movies_d4.py", title="Stream or Download Regional Movies Domain 4")
Torrent_Movies_Download = st.Page("torrent_download.py", title="Download Movie Torrents")
Torrent_Movies_Streaming = st.Page("torrent_streaming.py", title="Stream Movie Torrents")

pg = st.navigation([Movies_d1, Movies_d2,Movies_d3,Movies_d4, Torrent_Movies_Download, Torrent_Movies_Streaming],expanded=True)
st.set_page_config(page_title="Streaks Movies - Stream or download your Favorite movies", page_icon=":movie_camera:")
pg.run()