# web_utils.py

import requests
from lxml import html

class WebUtils:
    def __init__(self, payload=None):
        # Payload is optional; set a default if needed
        self.payload = payload if payload else {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                                                'Accept-Language': 'da, en-gb, en',
                                                'Accept-Encoding': 'gzip, deflate, br',
                                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                                                'Referer': 'https://www.google.com/'
                                                }

    def get_request(self, url):
        """
        Send an HTTP GET request to a URL and parse its HTML content.
        """
        try:
            response = requests.get(url, headers=self.payload)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                return tree
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
        return None

    def domain_finder(self, domain_keyword):
        """
        Find a working website matching the domain keyword by querying Google.
        """
        search_url = f'https://www.google.com/search?q={domain_keyword.replace(" ", "+")}'
        try:
            response = requests.get(search_url, headers=self.payload)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                links = tree.xpath('//h3/parent::a/@href')
                for each in links:
                    tree = self.get_request(each)
                    if tree is not None and tree.xpath('//form'):
                        return each
        except requests.RequestException as e:
            print(f"Error searching for {domain_keyword}: {e}")
        return None
