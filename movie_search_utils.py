# movie_search_utils.py

from web_utils import WebUtils

class MovieSearchUtils:
    def __init__(self):
        self.web_utils = WebUtils()  # Initialize the WebUtils instance

    def movie_search_isaimini(self, query):
        """
        Searches for movies on the isaimini website.
        """
        url = self.web_utils.domain_finder("isaimini")
        if not url:
            return {}, None

        dicto = {}
        search_url = url + f"mobile/search?find={query}&per_page=1"
        tree = self.web_utils.get_request(search_url)
        if tree:
            count = int(
                tree.xpath(
                    f'count(//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/text())'
                )
            )
            for i in range(count):
                dicto[
                    tree.xpath(
                        f'//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/text()'
                    )[i]
                ] = tree.xpath(
                    f'//div[@class="dir"]//a[contains(@href,"{url.replace("https://","").replace("/","")}")]/@href'
                )[
                    i + 1
                ]
        return dicto, url

    def movie_search_moviesda(self, query):
        """
        Searches for movies on the moviesda website.
        """
        url = self.web_utils.domain_finder("moviesda")
        if not url:
            return {}

        dicto = {}
        search_url = url + f"mobile/search?find={query}&per_page=1"
        tree = self.web_utils.get_request(search_url)
        if tree:
            count = int(tree.xpath("count(//div[@class='f']//a)"))
            for i in range(count):
                dicto[tree.xpath("//div[@class='f']//a/@title")[i]] = tree.xpath(
                    "//div[@class='f']//a/@href"
                )[i]
        return dicto

    def movie_search_movierulz(self, query):
        """
        Searches for movies on the movierulz website.
        """
        url = self.web_utils.domain_finder("movierulz")
        if not url:
            return {}

        dicto = {}
        search_url = url + f"search_movies?s={query}"
        tree = self.web_utils.get_request(search_url)
        if tree:
            count = int(tree.xpath('count(//div[@class="content home_style"]//li)'))
            for i in range(count):
                dicto[
                    tree.xpath("//div[@class='content home_style']//li//b/text()")[i]
                ] = tree.xpath(
                    "//div[@class='content home_style']//li//@href"
                )[i]
        return dicto

    def movie_search_1tamilyogi(self, query):
        """
        Searches for movies on the 1tamilyogi website.
        """
        url = self.web_utils.domain_finder("1tamilyogi")
        if not url:
            return {}

        dicto = {}
        search_url = url + f"?s={query}"
        tree = self.web_utils.get_request(search_url)
        if tree:
            count = int(tree.xpath('count(//ul[@class="recent-posts"]//li)'))
            for i in range(count):
                dicto[
                    tree.xpath("//ul[@class='recent-posts']//li//h2//a/text()")[i]
                ] = tree.xpath("//ul[@class='recent-posts']//li//h2//a/@href")[i]
        return dicto
