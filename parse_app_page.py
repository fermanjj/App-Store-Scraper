from bs4 import BeautifulSoup
import re
import sqlite3


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

        # price (this field isn't always there, i.e. TV apps)
        price_tag = soup.find('div', {'itemprop': 'price'})
        if price_tag is not None:
            self.output_dict['price'] = price_tag.text

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

        # languages (field is not always there)
        language_regex = r'Language[s]?: '
        language_tag = soup.find('span', text=re.compile(language_regex))
        if language_tag is not None:
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

        return self.output_dict

    # noinspection PyTypeChecker,SqlDialectInspection
    def write_out(self):
        """Override this method to write out
        however you'd like."""
        db = 'app_store_db'
        # using a with statement here automatically
        # closes the connection upon completion
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            # insert into main table
            main_table_insert_statement = """
            INSERT INTO app_store_main VALUES (
              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
              ?, ?, ?, ?, ?, ?
            )
            """
            cursor.execute(
                main_table_insert_statement,
                (
                    self.output_dict['app_id'],
                    self.output_dict['app_name'],
                    self.output_dict['description'],
                    self.output_dict['price'],
                    self.output_dict['category'],
                    self.output_dict['published_date'],
                    self.output_dict['last_updated_date'],
                    self.output_dict['version'],
                    self.output_dict['size'],
                    self.output_dict['seller'],
                    self.output_dict['copyright'],
                    self.output_dict['app_rating'],
                    self.output_dict['compatibility'],
                    self.output_dict['current_version_rating_value'],
                    self.output_dict['current_version_rating_review_count'],
                    self.output_dict['all_versions_rating_value'],
                    self.output_dict['all_versions_rating_review_count']
                )
            )

            languages_insert_statement = """
            INSERT INTO app_store_languages VALUES (?,?)
            """
            for language in self.output_dict['languages']:
                cursor.execute(
                    languages_insert_statement,
                    (self.output_dict['app_id'], language)
                )

            purchases_insert_statement = """
            INSERT INTO app_store_top_in_app_purchases VALUES 
            (?, ?, ?, ?)
            """
            for in_app_purchase in self.output_dict['top_in_app_purchases']:
                cursor.execute(
                    purchases_insert_statement,
                    (
                        self.output_dict['app_id'],
                        in_app_purchase['order'],
                        in_app_purchase['title'],
                        in_app_purchase['price']
                    )
                )

            customer_reviews_insert_statement = """
            INSERT INTO app_store_customer_reviews VALUES 
            (?, ?, ?, ?, ?)
            """
            for customer_review in self.output_dict['customer_reviews']:
                cursor.execute(
                    customer_reviews_insert_statement,
                    (
                        self.output_dict['app_id'],
                        customer_review['title'],
                        customer_review['rating'],
                        customer_review['user'],
                        customer_review['content']
                    )
                )

            conn.commit()

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
    p = ParseAppStorePage(open('App Store app example.htm').read())
    p.parse()
    p.write_out()
