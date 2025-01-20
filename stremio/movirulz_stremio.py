from utils import web_page_fetcher
from utils import streams_manager
import re

class Movierulz:
    """
    A class to search for movies on Movierulz, extract torrent links, and build STREAMS data structures.
    """

    @staticmethod
    def movie_search(title):
        """
        Search for movies on Movierulz and return a dictionary of movie titles and links.

        Args:
            title (str): The movie title to search for.

        Returns:
            dict: A dictionary with movie titles as keys and their corresponding links as values.
        """
        dicto = {}
        current_domain=web_page_fetcher.current_domain("https://www.5movierulz.rip/")
        query_url = f'{current_domain}search_movies?s={title.lower().replace(' ', '+')}'
        tree = web_page_fetcher.get_request(query_url)
        if tree is None:
            print(f'Error getting the webpage {query_url}')
            return dicto
        try:
            for i in range(0, int(tree.xpath('count(//div[@class=\"content home_style\"]//li)'))):
                dicto[tree.xpath('//div[@class=\"content home_style\"]//li//b/text()')[i]] = tree.xpath('//div[@class=\"content home_style\"]//li//@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed for {current_domain}: {e}")
        return dicto

    @staticmethod
    def movie_torrents(movie_link):
        """
        Extract torrent links for a selected movie from Movierulz.

        Args:
            selected_movie_link (str): The link to the movie page.

        Returns:
            dict: A dictionary with torrent file names as keys and their download links as values.
        """
        dicto = {}
        # Pattern to match website URLs, " - ", and "(2025)"
        pattern = r"Full|Movie|Watch|Online|Free"
        tree = web_page_fetcher.get_request(movie_link)
        if tree is None:
            print(f'Error getting the webpage {movie_link}')
            return dicto
        try:
            for i in range(0, int(tree.xpath('count(//span[contains(text(),"Torrent")]/following::a[contains(@href, "magnet")]//small/text())'))):
                text=re.sub(pattern,"",tree.xpath('//h2[@class="entry-title"]/text()')[0])+" "+tree.xpath('//span[contains(text(), "Torrent")]/following::a[contains(@href, "magnet")]//small/text()')[i]
                dicto[re.sub(r'\s+', ' ', text).strip()] = tree.xpath('//span[contains(text(), "Torrent")]/following::a[contains(@href, "magnet")]/@href')[i]
        except Exception as e:
            print(f"Error while Extracting the elements/ No proper Page formed for {movie_link}: {e}")
        return dicto

    @staticmethod
    def movierulz(title, movie_id):
        """
        Search for movies, fetch torrent links, and create STREAMS data structure.

        Args:
            title (str): The movie title to search for.
            movie_id (str): Unique identifier for the movie.

        Returns:
            dict: The STREAMS data structure.
        """
        results = {}
        search_results = Movierulz.movie_search(title)
        for link in search_results.values():
            results.update(Movierulz.movie_torrents(link))
        return streams_manager.create_streams(results)