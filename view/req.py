#!/usr/bin/env python3

import enum
import os

from flask import request
from flask_security import current_user
import sqlalchemy as sqla

from model import get_session
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema.feeds import Language

class Feed(enum.Enum):
    FULL = "Full"
    MAGIC = "Magic"
    SURPRISE = "Surprise"

class Timeunit(enum.Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

def get_feed():
    return Feed[request.args.get('feed', default=Feed.FULL.name)]

def get_langs():
    res = [Language[e] for e in request.args.getlist('lang')]
    if set(displayed_languages(current_user.UserID)) <= set(res):
        res = []
    return res

def get_page():
    if get_timeunit_new() == get_timeunit_old():
        return request.args.get('page', default=0, type=int)
    else:
        return 0

def get_tags():
    return request.args.getlist('tag')

def get_timeunit():
    return get_timeunit_new()

def get_timeunit_old():
    return Timeunit[request.args.get('timeunit', default=Timeunit.DAY.name)]

def get_timeunit_new():
    return Timeunit[request.args.get('timeunit_new', default=get_timeunit_old().name)]

def base_context():
    context = dict()

    # topnav.html.
    context['feed'] = get_feed()
    context['timeunit'] = get_timeunit()
    context['page'] = get_page()
    context['langs'] = get_langs()
    context['tags'] = get_tags()

    # sidenav.html.
    context['langs_disp'] = displayed_languages(current_user.UserID)
    context['tags_disp'] = displayed_tags(current_user.UserID)

    # sidenav.html.
    context['feeds_all']=all_feeds()
    context['tags_all']=all_tags(current_user.UserID)

    # sidenav.html.
    dir_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "clf.d",
        str(current_user.UserID)
    ))
    context['magic_exists'] = os.path.isdir(dir_path)

    # sidenav.html.
    context['enum_feed'] = Feed
    context['enum_timeunit'] = Timeunit

    return context

def all_feeds():
    q = sqla.select(
        orm_feeds.Feed
    ).order_by(
        sqla.collate(orm_feeds.Feed.Title, "NOCASE")
    )

    with get_session() as session:
        return [e[0] for e in session.execute(q)]

def all_tags(user_id):
    q = sqla.select(
        orm_feeds.Tag
    ).where(
        orm_feeds.Tag.UserID == user_id
    ).order_by(
        sqla.collate(orm_feeds.Tag.Name, "NOCASE")
    )

    with get_session() as session:
        return [e[0] for e in session.execute(q)]

def displayed_languages(user_id):
    q = sqla.select(
        orm_feeds.Feed.Language,
    ).where(
        orm_feeds.Feed.users.any(orm_users.User.UserID == user_id),
    ).order_by(
        orm_feeds.Feed.Language
    ).distinct()

    with get_session() as session:
        return [Language[e.Language] for e in session.execute(q)]

def displayed_tags(user_id):
    q = sqla.select(
        orm_feeds.Tag.Name,
    ).where(
        orm_feeds.Tag.UserID == user_id,
        orm_feeds.Tag.feeds.any(orm_feeds.Feed.users.any(orm_users.User.UserID == user_id)),
    ).order_by(
        orm_feeds.Tag.Name,
    ).distinct()

    with get_session() as session:
        return [e.Name for e in session.execute(q)]
