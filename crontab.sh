00 * * * * sqlite3 steins.db ".backup 'steins.db.0'"; python3 /var/www/html/steins-feed/steins_feed.py; sqlite3 steins.db ".backup 'steins.db.1'"
