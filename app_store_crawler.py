"""Given a category, go through the app store links and
parse every page.
"""

START_URL = 'https://itunes.apple.com/us/genre/ios-games/id6014?mt=8'


class CrawlAppStore:
    def __init__(self, start_url=''):
        """Starts crawling the App store at
        a give start url. You can provide a start
        url when instantiating this class or you
        can change the START_URL var to be your
        start.

        :param start_url:
        :type start_url: str
        """

        if not start_url:
            self.start_url = START_URL
        else:
            self.start_url = start_url

    def crawl(self):
        pass


if __name__ == '__main__':
    c = CrawlAppStore()
