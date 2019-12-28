sqlite3 /var/www/html/steins-feed/steins.db ".backup '/var/www/html/steins-feed/steins.db.0'"
python3 /var/www/html/steins-feed/steins_feed.py >& /var/www/html/steins-feed/steins_feed.log
python3 /var/www/html/steins-feed/steins_magic.py >& /var/www/html/steins-feed/steins_magic.log
