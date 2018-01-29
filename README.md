# App Store Scraper

A basic parser for an app store page using BeautifulSoup.

A basic crawler for searching categories on the app store.

# NOTE:exclamation:

The Apple app store has completely redesigned their page. It is most likely that the parser aspect of this repo does not work as is.

## Getting Started

* Install Python (built using 3.6).

* Create and activate a virtualenv.

* `pip install -r requirements.txt`

* Make sure you've got a sqlite database setup with the name: `app_store_db` (see the `create table statements.sql` file for the schema.

* Run `python app_store_crawler.py` to start populating the db with links

* Then switch over to crawling the app pages from the db (Note that the app store has limits)

* Visualize things using `python app_store_visualization.py`

## How to use

You'll need to create a database to communicate with. (This isn't absolutely necessary but if you don't, you'll have to re-implement a few things)

I've created some simple sql create statements to get the basic tables. This uses sqlite.

