#!/usr/bin/env python3

import datetime
import os

from flask import request
from flask_security import current_user
import sqlalchemy as sqla

from model import get_session
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema.feeds import Language
from view.home import unit as home_unit
from view.home import wall as home_wall

def get_wall():
    wall_name = request.args.get(
        "feed",
        default = home_wall.WallMode.CLASSIC.name,
        type=str,
    )
    return home_wall.WallMode[wall_name]

def get_langs():
    res = [Language[e] for e in request.args.getlist('lang')]
    if set(displayed_languages(current_user.UserID)) <= set(res):
        res = []
    return res

def get_page():
    current_time = datetime.datetime.now()
    current_time = home_unit.round_to(current_time, get_timeunit())

    if get_timeunit() == get_timeunit(old=True):
        s = request.args.get('page', default=None, type=str)
        if s:
            return datetime.datetime.fromisoformat(s)
        else:
            return current_time
    else:
        return current_time

def get_tags():
    return request.args.getlist('tag')

def get_timeunit(old: bool=False):
    if old:
        k = "timeunit"
        v = home_unit.UnitMode.DAY.name
    else:
        k = "timeunit_new"
        v = get_timeunit(old=True).name

    unit_name = request.args.get(
        k,
        default = v,
        type=str,
    )

    return home_unit.UnitMode[unit_name]

def base_context():
    context = dict()

    # topnav.html.
    context['feed'] = get_wall()
    context['timeunit'] = get_timeunit()
    context['page'] = get_page()
    context['prev_page'] = home_unit.decrement_to(get_page(), get_timeunit())
    context['next_page'] = home_unit.increment_to(get_page(), get_timeunit())
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
    context['enum_feed'] = home_wall.WallMode
    context['enum_timeunit'] = home_unit.UnitMode

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
    ).join(
        orm_feeds.Feed.users
    ).where(
        orm_users.User.UserID == user_id,
    ).order_by(
        orm_feeds.Feed.Language,
    ).distinct()

    with get_session() as session:
        return [Language[e.Language] for e in session.execute(q)]

def displayed_tags(user_id):
    q = sqla.select(
        orm_feeds.Tag.Name,
    ).join(
        orm_feeds.Tag.feeds
    ).join(
        orm_feeds.Feed.users
    ).where(
        orm_feeds.Tag.UserID == user_id,
        orm_users.User.UserID == user_id,
    ).order_by(
        orm_feeds.Tag.Name,
    ).distinct()

    with get_session() as session:
        return [e.Name for e in session.execute(q)]
