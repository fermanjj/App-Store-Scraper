from bs4 import BeautifulSoup
import pprint
import re


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
            published_date='',
            last_updated_date='',
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
        # published_date: 2016-11-23 09:39:55
        # last_updated_date: Aug 30, 2017
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

        # price
        self.output_dict['price'] = soup.find('div', {'itemprop': 'price'}).text

        # category
        self.output_dict['category'] = soup.find('span', {'itemprop': 'applicationCategory'}).text

        # date_published and last_update_date
        published_date_span = soup.find('span', {'itemprop': 'datePublished'})
        self.output_dict['published_date'] = published_date_span['content']
        self.output_dict['last_updated_date'] = published_date_span.text

        # version
        self.output_dict['version'] = soup.find('span', {'itemprop': 'softwareVersion'}).text

        # size
        size_tag = soup.find('span', text='Size: ')
        self.output_dict['size'] = size_tag.next_sibling

        # languages
        language_tag = soup.find('span', text='Languages: ')
        all_languages = language_tag.next_sibling.split(', ')
        self.output_dict['languages'] = all_languages

        # seller
        seller_tag = soup.find('span', {'itemprop': 'author'})
        self.output_dict['seller'] = seller_tag.span.text

        # copyright
        self.output_dict['copyright'] = soup.find('li', {'class': 'copyright'}).text

        # app rating
        self.output_dict['app_rating'] = soup.find('div', {'class': 'app-rating'}).text

        # compatibility
        compatibility = soup.find('span', {'itemprop': 'operatingSystem'}).text.replace('\xa0', ' ')
        self.output_dict['compatibility'] = compatibility

        # customer ratings (these fields may not appear)

        # current version rating
        ratings_current_version_tag = soup.find('div', text='Current Version:')
        # check to make sure we found it
        if ratings_current_version_tag is not None:
            # if so, parse
            div = ratings_current_version_tag.find_next('div')
            # check for the rating value in the page
            rating_value_span = div.find('span', {'itemprop': 'ratingValue'})
            if rating_value_span is not None:
                self.output_dict['current_version_rating_value'] = rating_value_span.text
            else:
                # otherwise, parse it out of the aria-label
                self.output_dict['current_version_rating_value'] = self.parse_rating(div['aria-label'])
            # parse the rating count
            rating_count_span = div.find('span', {'class': 'rating-count'})
            rating_count = rating_count_span.text.replace(' Ratings', '')
            self.output_dict['current_version_rating_review_count'] = rating_count

        # all versions rating
        ratings_all_versions_tag = soup.find('div', text='All Versions:')
        # check to make sure we found it
        if ratings_all_versions_tag is not None:
            # if so, parse
            div = ratings_all_versions_tag.find_next('div')
            # check for the rating value in the page
            rating_value_span = div.find('span', {'itemprop': 'ratingValue'})
            if rating_value_span is not None:
                self.output_dict['all_versions_rating_value'] = rating_value_span.text
            else:
                # otherwise, parse it out of the aria-label
                self.output_dict['all_versions_rating_value'] = self.parse_rating(div['aria-label'])
            # parse the rating count
            rating_count_span = div.find('span', {'class': 'rating-count'})
            rating_count = rating_count_span.text.replace(' Ratings', '')
            self.output_dict['all_versions_rating_review_count'] = rating_count

        # top in app purchases (This field may not be there)
        in_app_purchases_div = soup.find('div', {'metrics-loc': 'Titledbox_Top In-App Purchases'})
        if in_app_purchases_div is not None:
            in_app_purchases = []
            for i, li in enumerate(in_app_purchases_div.find('ol').find_all('li'), 1):
                title = li.find('span', {'class': 'in-app-title'}).text
                price = li.find('span', {'class': 'in-app-price'}).text
                in_app_purchases.append({'title': title, 'price': price, 'order': i})
            self.output_dict['top_in_app_purchases'] = in_app_purchases

        # customer reviews (this may not be there)
        customer_reviews_div = soup.find('div', {'class': 'customer-reviews'})
        if customer_reviews_div is not None:
            all_customer_reviews = []
            for review in customer_reviews_div.find_all('div', {'class': 'customer-review'}):
                title = review.find('span', {'class': 'customerReviewTitle'}).text
                rating_div = review.find('div', {'class': 'rating'})
                rating_parsed = self.parse_rating(rating_div['aria-label'])

                # get the user info and clean it up
                user_span = review.find('span', {'class': 'user-info'}).text
                user_clean = re.sub('\s\s', ' ', user_span)
                while '  ' in user_clean:
                    user_clean = re.sub('\s\s', ' ', user_clean)
                user_clean = re.sub('^by ', '', user_clean).strip()

                content = review.find('p', {'class': 'content'}).text

                all_customer_reviews.append({
                    'title': title, 'rating': rating_parsed,
                    'user': user_clean, 'content': content
                })
            self.output_dict['customer_reviews'] = all_customer_reviews

        # testing
        pprint.pprint(self.output_dict)

    @staticmethod
    def parse_rating(rating):
        """Takes a string like "4 and a half stars, 736 Ratings"
        and parses the number of ratings to be 4.5

        :param rating:
        :type rating: str
        :return: A string of the rating
        :rtype: str
        """
        # searches for the rating in the string and the word half
        regex = r'(?P<rating>[0-9]) (?:(?P<half>and a half stars)|(?P<not_half>star[s]?))'

        # run the regex search
        rating_search = re.search(regex, rating)

        # assign the rating value
        rating_value = rating_search.group('rating')
        # if the word half appeared, then add .5 to the rating
        if rating_search.group('half'):
            rating_value += '.5'

        return rating_value


if __name__ == '__main__':
    ParseAppStorePage(open('App Store app example.htm').read()).parse()
