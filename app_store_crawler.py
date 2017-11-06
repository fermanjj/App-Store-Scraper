import sqlite3
import threading
import re
from urllib import parse
from string import ascii_uppercase
import requests
from bs4 import BeautifulSoup
from parse_app_page import ParseAppStorePage


# noinspection SqlDialectInspection
class CrawlAppStore:

    db = 'app_store_db'

    def __init__(self):
        self.db_lock = threading.Lock()
        self.search_semaphore = threading.BoundedSemaphore(8)

    def fetch_category_crawl_prog(self, url):
        """Gets the current progress of the crawl for
        the categories scraper.

        :param url:
        :type url: str
        :rtype: tuple
        """
        with self.db_lock:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()

                select_statement = """
                SELECT * FROM app_store_crawl_categories_prog
                WHERE url = ?
                """
                cursor.execute(select_statement, (url,))
                result = cursor.fetchall()
                if len(result) == 0:
                    return 1, 'A'
                else:
                    return int(result[0][0]), result[0][1]

    def crawl_category_page(self, start_url):
        """Given a category/sub-category page,
        it attempts to go through every page, grabbing
        all links and writing them out.

        :param start_url:
        :type start_url: str
        """
        # get the last starting position of the scrape
        # from this start url
        page_count, letter = self.fetch_category_crawl_prog(start_url)

        # clean the start url
        start_url_parse = parse.urlparse(start_url)
        cleaned_start_url = parse.urlunparse((
            start_url_parse.scheme, start_url_parse.netloc,
            start_url_parse.path, start_url_parse.params, '', ''
        ))

        # create a duplicate list of uppercase letters
        letters = [x for x in ascii_uppercase]

        # loop through the letters and take out those we've already
        # searched, based on the last starting position
        for x in range(len(letters)):
            if letter == letters[x]:
                break
            letters.pop(x)

        # here we override the earlier assignment of letter
        # because we're now at the point we want to start at.
        for letter in letters:
            # the idea here is to loop through letters A-Z
            # and pages 1-* per letter
            while 1:
                new_url = (
                    cleaned_start_url +
                    '?letter={}&page={}'.format(letter, page_count)
                )
                source_page = self.get_request(new_url)
                links = self.parse_category_page(source_page)
                if not links:
                    break
                self.write_out_links(links)
                page_count += 1
                self.save_category_crawl_prog(start_url, letter, page_count)
            page_count = 1

    def write_out_links(self, links):
        """Write out a list of links to the db
        which will get used later for searching and parsing.

        :param links:
        :type links: list
        :return:
        """
        with self.db_lock:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                insert_statement = """
                INSERT INTO app_store_app_urls
                VALUES (?)
                """
                for link in links:
                    cursor.execute(insert_statement, (link,))
                conn.commit()

    @staticmethod
    def parse_category_page(source):
        """Parses the html from a categories page
        and looks for all the links to go to.
        If there aren't any, then returns an empty list.

        :param source:
        :type source: str
        :rtype: list
        """
        soup = BeautifulSoup(source, 'html.parser')
        href_regex = r'https://itunes\.apple\.com/us/app/.*/id[0-9]*\?mt=8'
        all_links = soup.find_all('a', {'href': re.compile(href_regex)})
        return [x['href'] for x in all_links]

    def save_category_crawl_prog(self, url, letter, page):
        """Writes out the progress of the categories crawl
        to the db.

        :param url:
        :type url: str
        :param letter:
        :type letter: str
        :param page:
        :type page: str
        """
        with self.db_lock:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                update_statement = """
                REPLACE INTO app_store_crawl_categories_prog
                VALUES (?, ?, ?)
                WHERE url = ?
                """
                cursor.execute(
                    update_statement,
                    (url, letter, page, url)
                )
                conn.commit()

    @staticmethod
    def get_request(url):
        """Sends a request to the url and returns
        the html.

        :param url:
        :type url: str
        :rtype: str
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/62.0.3202.75 Safari/537.36'}
        return requests.get(url, headers=headers).text

    def crawl_app_pages_from_db(self):
        """Fetch the list of urls from the db and search."""
        with self.db_lock:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM app_store_app_urls')
                results = [x[0] for x in cursor.fetchall()]
        self.crawl_app_pages(results)

    def remove_searched_url(self, url):
        """Remove a url from the app_urls table.

        :param url:
        :type url: str
        """
        with self.db_lock:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                delete_statement = """
                DELETE FROM app_store_app_urls WHERE url = ?
                """
                cursor.execute(delete_statement, (url,))
                conn.commit()

    def search_app_page(self, url):
        """Search a single url, parse and write out.

        :param url:
        :type url: str
        """
        source = self.get_request(url)
        parsed = ParseAppStorePage(source)
        try:
            parsed.parse()
        except Exception as e:
            print(url)
            raise e
        with self.db_lock:
            parsed.write_out()
        self.remove_searched_url(url)
        self.search_semaphore.release()

    def crawl_app_pages(self, url_list):
        """Given a list of urls, starts crawling them
        and uses the parser to parse and write out.

        :param url_list:
        :type url_list: list
        """
        for url in url_list:
            self.search_semaphore.acquire()
            threading.Thread(
                target=self.search_app_page, daemon=1,
                args=(url,)
            ).start()


if __name__ == '__main__':

    category = 'https://itunes.apple.com/us/genre/ios-games/id6014?mt=8'
    c = CrawlAppStore()
    # c.crawl_category_page(category)
    c.crawl_app_pages_from_db()
