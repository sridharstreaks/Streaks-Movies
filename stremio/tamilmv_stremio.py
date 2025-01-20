from utils import web_page_fetcher
from utils import streams_manager
import re
from typing import List

class Tamilmv:
    """
    A class to search for movies on TamilMV, extract torrent links, and build STREAMS data structures.
    """

    @staticmethod
    def movie_search(title):
        """
        Search for movies on TamilMV and return a dictionary of movie titles and links.

        Args:
            title (str): The movie title to search for.

        Returns:
            dict: A dictionary with movie titles as keys and their corresponding links as values.
        """
        dicto = {}
        current_domain=web_page_fetcher.current_domain("https://www.1tamilmv.com/")
        query_url = f'{current_domain}index.php?/search/&q=\"{title.replace(" ","%20")}\"&type=forums_topic&quick=1&search_and_or=and&search_in=titles&sortby=relevancy'
        tree = web_page_fetcher.get_request(query_url)
        if tree is None:
            print(f'Error getting the webpage {query_url}')
            return dicto
        try:
            titles = tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a//text()')
            links = tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a/@href')
            for i in range(len(titles)):
                if not any(
                    word.lower() in titles[i].lower()
                    for word in ['OTT', 'Trailer', 'Soundtrack', 'Master Quality', 'Lyrical', 'GDRIVE', 
                                 'Ai Upscaled', 'MUSIC VIDEO', 'Video Songs', 'Video Song', 'YT-DL', 
                                 'Musical', 'Audio Launch', 'Teaser', 'Sneak Peek']
                ):
                    dicto[titles[i]] = links[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed for {current_domain}: {e}")
        return dicto

    @staticmethod
    def movie_torrents(movie_link):
        """
        Extract torrent links for a selected movie from TamilMV.

        Args:
            selected_movie_link (str): The link to the movie page.

        Returns:
            dict: A dictionary with torrent file names as keys and their download links as values.
        """
        dicto = {}
        # Pattern to match website URLs, " - ", and "(2025)"
        pattern = r"www\.[^ ]+\s+-\s+| - |\.torrent|\.mkv|\.mp4|\.avi"
        tree = web_page_fetcher.get_request(movie_link)
        if tree is None:
            print(f'Error getting the webpage {movie_link}')
            return dicto
        try:
            torrent_titles = tree.xpath('//a[@data-fileext="torrent"]//span/text()')
            torrent_links = tree.xpath('//a[@class="skyblue-button"]/@href')
            for i in range(len(torrent_titles)):
                dicto[re.sub(pattern, " ", torrent_titles[i]).strip()] = torrent_links[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed for {movie_link}: {e}")
        return dicto

    @staticmethod
    def tamilmv(title, movie_id)-> List[dict]:
        """
        Search for movies, fetch torrent links, and create STREAMS data structure.

        Args:
            title (str): The movie title to search for.
            movie_id (str): Unique identifier for the movie.

        Returns:
            dict: The STREAMS data structure.
        """
        results = {}
        search_results = Tamilmv.movie_search(title)
        for link in search_results.values():
            results.update(Tamilmv.movie_torrents(link))
        return streams_manager.create_streams(results)