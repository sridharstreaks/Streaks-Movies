import requests
from lxml import html

class web_utils:
    def __init__(self):
        self.payload = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Accept-Language': 'da, en-gb, en',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }

    def get_request(self, url):
        """Fetches the HTML content of a given URL and parses it into an lxml tree."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                return tree
            else:
                print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while fetching URL: {url}, Error: {e}")
        return None
    
    def get_url(self, url):
        """Fetches the HTML content of a given URL and parses it into an lxml tree."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                current_url = response.url
                return current_url
            else:
                print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while fetching URL: {url}, Error: {e}")
        return None

    def domain_finder(self, domain_keyword):
        """Finds a working website based on the domain keyword, ignoring faulty ones."""
        url = f'https://www.google.com/search?q={domain_keyword.replace(" ", "+")}'
        try:
            response = requests.get(url, headers=self.payload)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                links = tree.xpath('//h3/parent::a/@href')
                for each in links:
                    tree = self.get_request(each)
                    if tree is not None and tree.xpath('//form') != []:
                        return each
            else:
                print(f"Failed to perform Google search, Status Code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred during domain search: {e}")
        return None