create table app_store_customer_reviews
(
	app_id TEXT,
	title TEXT,
	rating TEXT,
	user TEXT,
	content TEXT
)
;

create table app_store_languages
(
	app_id TEXT,
	language TEXT
)
;

create table app_store_main
(
	app_id TEXT,
	app_name TEXT,
	description TEXT,
	price TEXT,
	category TEXT,
	published_date TEXT,
	last_updated_date TEXT,
	version TEXT,
	size TEXT,
	seller TEXT,
	copyright TEXT,
	app_rating TEXT,
	compatibility TEXT,
	current_version_rating_value TEXT,
	current_version_rating_review_count TEXT,
	all_versions_rating_value TEXT,
	all_versions_rating_review_count TEXT
)
;

create table app_store_top_in_app_purchases
(
	app_id TEXT,
	"order" TEXT,
	title TEXT,
	price TEXT
)
;

