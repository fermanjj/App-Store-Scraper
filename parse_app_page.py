from bs4 import BeautifulSoup
import pprint


class InvalidPageException(Exception):
    """Raised when we've hit a page that doesn't have the necessary
    values to parse, i.e. the app ID."""


class ParseAppStorePage:
    def __init__(self, source_page):
        """Takes in the html from an app store page as a string.

        Call the parse method to parse and return a
        dict object of the parsed page.

        :param source_page:
        :type source_page: str
        """
        self.source_page = source_page

        self.output_dict = dict(
            app_id='',
            app_name='',
            description='',
            price='',
            category='',
            last_updated='',
            version='',
            size='',
            languages=[],
            seller='',
            copyright='',
            app_rating='',
            compatibility='',
            current_version_rating_value='',
            current_version_rating_review_count='',
            all_versions_rating_value='',
            all_versions_rating_review_count='',
            top_in_app_purchases=[],
            customer_reviews=[]
        )

    def parse(self):
        soup = BeautifulSoup(self.source_page, 'html.parser')

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

        # we check to make sure we found an app ID
        app_id_tag = soup.find('meta', {'name': 'apple:content_id'})
        if app_id_tag is None:
            raise InvalidPageException("No App ID found.")
        # assign app id value here
        self.output_dict['app_id'] = app_id_tag['content']

        # app name
        self.output_dict['app_name'] = soup.find('h1', {'itemprop': 'name'}).text

        # get description div
        description_div = soup.find('div', {'metrics-loc': 'Titledbox_Description'})
        # get description paragraph and decode raw html
        description_raw = description_div.p.decode_contents()
        # assign description, replacing break tags as line feeds
        self.output_dict['description'] = description_raw.replace('<br/>', '\n')

        # testing
        pprint.pprint(self.output_dict)


if __name__ == '__main__':
    ParseAppStorePage(open('App Store app example.htm').read()).parse()
