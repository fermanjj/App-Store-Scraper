from bs4 import BeautifulSoup


class ParseAppStorePage:
    def __init__(self, source_page):
        """Takes in the html from an app store page as a string.

        Call the parse method to parse and return a
        dict object of the parsed page.

        :param source_page:
        :type source_page: str
        """
        self.source_page = source_page

    def parse(self):
        soup = BeautifulSoup(self.source_page)

        # fields we will capture
        # app id: 1121971067
        # app name: Archery King
        # description: Worlds #1 Archery Game...
        # price: Free
        # category: Games
        # updated: Aug 30, 2017
        # version: 1.0.18
        # size: 142 MB
        # languages: English, Arabic, ...
        # seller: Miniclip SA
        # copyright?:
        # app_rating: Rated 4+
        # compatibility: Requires iOS 7.0 ...
        # current_version_rating_value: 4.40082
        # current_version_rating_review_count: 736
        # all_versions_rating_value: ?
        # all_versions_rating_review_count: 10312
        # top_in_app_purchases: Premium Golden ... $1.99
        # customer_reviews: title, rating, written_by, content


if __name__ == '__main__':
    ParseAppStorePage(open('App Store app example.htm').read())
