sqlite3 /var/www/html/steins-feed/steins.db ".backup '/var/www/html/steins-feed/steins.db.0'"
python3 /var/www/html/steins-feed/steins_feed.py
sqlite3 /var/www/html/steins-feed/steins.db ".backup '/var/www/html/steins-feed/steins.db.1'"
