from utils import web_page_fetcher
from utils import streams_manager
import re

class Tamilblasters:
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
        current_domain=web_page_fetcher.current_domain("https://www.1tamilblasters.net/")
        query_url = f'{current_domain}index.php?/search/&q=\"{title.replace(' ', '%20')}\"&updated_after=any&sortby=relevancy&search_in=titles'
        tree = web_page_fetcher.get_request(query_url)
        if tree is None:
            print(f'Error getting the webpage {query_url}')
            return dicto
        try:
            for i in range(0,int(tree.xpath('count(//ol//h2[contains(@class,"StreamItem_title")]//a//text())'))):
                if not any(word.lower() in tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a//text()')[i].lower() for word in ['OTT', 'Trailer', 'Soundtrack', 'Master Quality', 'Lyrical', 'GDRIVE', 
                                 'Ai Upscaled', 'MUSIC VIDEO', 'Video Songs', 'Video Song', 'YT-DL', 
                                 'Musical', 'Audio Launch', 'Teaser', 'Sneak Peek']):
                    dicto[tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a//text()')[i]]=tree.xpath('//ol//h2[contains(@class,"StreamItem_title")]//a/@href')[i]
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
            for i in range(0, int(tree.xpath('count(//a[@class="ipsAttachLink"])'))):
                dicto[re.sub(pattern,"",tree.xpath('//a[@class="ipsAttachLink"]/text()')[i])] = tree.xpath('//a[@class="magnet-plugin"]/@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed for {movie_link}: {e}")
        return dicto

    @staticmethod
    def tamilblasters(title, movie_id):
        """
        Search for movies, fetch torrent links, and create STREAMS data structure.

        Args:
            title (str): The movie title to search for.
            movie_id (str): Unique identifier for the movie.

        Returns:
            dict: The STREAMS data structure.
        """
        results = {}
        search_results = Tamilblasters.movie_search(title)
        for link in search_results.values():
            results.update(Tamilblasters.movie_torrents(link))
        return streams_manager.create_streams(results)