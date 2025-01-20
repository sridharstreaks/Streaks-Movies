import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError, ServerTimeoutError
from asyncio.exceptions import TimeoutError
from lxml import html
import urllib3
import json
import re

class web_page_fetcher:
    MAX_RETRIES = 3  # Maximum number of retries
    TIMEOUT = 10  # Timeout in seconds for each request
    """
    A class to fetch HTML content of a webpage asynchronously.
    """

    @staticmethod
    async def fetch_page_url(url):
        """
        Fetch the current domain name of the website asynchronously.

        Args:
            url (str): The URL of the webpage to fetch.

        Returns:
            (str): Current domain URL of the website, or None if the request fails.
        """
        for attempt in range(web_page_fetcher.MAX_RETRIES):
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=web_page_fetcher.TIMEOUT)) as session:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return str(response.url)  # Return the parsed HTML tree
                        else:
                            return print(f"Failed to fetch current domain for {url}. HTTP status: {response.status}")
                except (ClientConnectorError, ServerTimeoutError, TimeoutError) as e:
                    print(f"Attempt {attempt + 1}/{web_page_fetcher.MAX_RETRIES}: Error fetching {url}: {e}")
                    if attempt + 1 == web_page_fetcher.MAX_RETRIES:
                        return print(f"Failed to fetch {url} after {web_page_fetcher.MAX_RETRIES} attempts.")
                except Exception as e:
                    return f"An unexpected error occurred: {e}"

    @staticmethod
    def current_domain(url):
        """
        Wrapper function to run the async function in a synchronous context.

        Args:
            url (str): The URL of the webpage to get domain.

        Returns:
            str: The Name of the current domain or an error message.
        """
        return asyncio.run(web_page_fetcher.fetch_page_url(url))
    # def current_domain(url):
    #     """
    #     Fetch the current domain name of the website.

    #     Args:
    #         url (str): The URL of the webpage to fetch.

    #     Returns:
    #         (str): current domain url of the website.
    #     """
    #     http = urllib3.PoolManager()
    #     try:
    #         response = http.request('GET', url)
    #         if response.status == 200:
    #             return response.url
    #     finally:
    #         # Ensure the connection pool is closed
    #         http.clear()

    @staticmethod
    async def fetch_page_html(url):
        """
        Fetch the entire HTML content of a page asynchronously.

        Args:
            url (str): The URL of the webpage to fetch.

        Returns:
            lxml.html.HtmlElement or str: The HTML content of the page as an lxml tree if successful, 
            or an error message.
        """
        for attempt in range(web_page_fetcher.MAX_RETRIES):
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=web_page_fetcher.TIMEOUT)) as session:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            tree = html.fromstring(await response.text())
                            return tree  # Return the parsed HTML tree
                        else:
                            return print(f"Failed to fetch current domain for {url}. HTTP status: {response.status}")
                except (ClientConnectorError, ServerTimeoutError, TimeoutError) as e:
                    print(f"Attempt {attempt + 1}/{web_page_fetcher.MAX_RETRIES}: Error fetching {url}: {e}")
                    if attempt + 1 == web_page_fetcher.MAX_RETRIES:
                        return print(f"Failed to fetch {url} after {web_page_fetcher.MAX_RETRIES} attempts.")
                except Exception as e:
                    return f"An unexpected error occurred: {e}"

    @staticmethod
    def get_request(url):
        """
        Wrapper function to run the async function in a synchronous context.

        Args:
            url (str): The URL of the webpage to fetch.

        Returns:
            lxml.html.HtmlElement or str: The HTML content of the page or an error message.
        """
        return asyncio.run(web_page_fetcher.fetch_page_html(url))


class imdb_retriver:
    """
    A class to fetch movie titles from IMDb's suggestion API.
    """

    @staticmethod
    def fetch_movie_title(movie_id):
        """
        Fetch the movie title using its IMDb movie ID.

        Args:
            movie_id (str): The IMDb movie ID.

        Returns:
            str: The title of the movie if successful, or an error message.
        """
        http = urllib3.PoolManager()
        url = f'https://v2.sg.media-imdb.com/suggestion/h/{movie_id}.json'

        try:
            response = http.request('GET', url)
            if response.status == 200:
                movie_data = json.loads(response.data)
                return movie_data['d'][0]['l']  # Return the movie title
            else:
                return f"Failed to fetch movie title. HTTP status: {response.status}"
        except Exception as e:
            return f"An error occurred: {e}"
        

class streams_manager:
    """
    A class to manage and create STREAMS data structures for movies and magnet links.
    """

    @staticmethod
    def extract_info_hash(magnet_link):
        """
        Extract the info hash from a magnet link.

        Args:
            magnet_link (str): The magnet link containing the info hash.

        Returns:
            str or None: The info hash if found, otherwise None.
        """
        # Regular expression to match the info hash in a magnet link
        regex = r'btih:([a-fA-F0-9]{40})'
        match = re.search(regex, magnet_link)

        if match:
            return match.group(1).lower()  # Return the captured info hash in lowercase
        return None

    @staticmethod
    def create_streams(movie_dict):
        """
        Create a STREAMS dictionary structure from a movie dictionary.

        Args:
            movie_dict (dict): Dictionary with movie titles as keys and magnet links as values.
            movie_id (str): Unique identifier for the movie.

        Returns:
            dict: The STREAMS data structure containing movies and their info hashes.
        """
        # Initialize the STREAMS structure with 'movie' as top-level key
        streams = []

        # For each movie in the dictionary, extract the infoHash and build the structure
        for movie, magnet_link in movie_dict.items():
            info_hash = streams_manager.extract_info_hash(magnet_link)
            if info_hash:
                # For each movie ID, add the list of dictionaries with infoHash
                
                streams.append({
                    'title': movie,
                    'infoHash': info_hash
                })
        return streams