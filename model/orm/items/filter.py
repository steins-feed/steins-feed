#!/usr/bin/env python3

from model.orm import feeds as orm_feeds
from model.orm import items as orm_items
from model.orm import users as orm_users

def filter_display(q, user_id):
    item_feed = orm_items.Item.feed
    q = q.join(item_feed)

    feed_users = orm_feeds.Feed.users.and_(
        orm_users.User.UserID == user_id,
    )
    q = q.join(feed_users)

    return q

