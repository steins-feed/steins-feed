#!/usr/bin/env python3


import datetime
import flask
import flask_security
import os
import sqlalchemy as sqla
import typing

import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from view.feed import db as feed_db
from view.home import unit as home_unit
from view.home import wall as home_wall
from view.overview import db as overview_db
from view.tag import db as tag_db

def get_wall() -> home_wall.WallMode:
    wall_name = flask.request.args.get(
        "feed",
        default = home_wall.WallMode.CLASSIC.name,
    )
    return home_wall.WallMode[wall_name]

def get_langs() -> typing.List[schema_feeds.Language]:
    user = flask_security.current_user

    res = [
        schema_feeds.Language[e]
        for e in flask.request.args.getlist("lang")
    ]

    if set(overview_db.all_langs(user)) <= set(res):
        res = []

    return res

def get_page() -> datetime.datetime:
    timeunit = get_timeunit()
    timeunit_old = get_timeunit(old=True)

    current_time = datetime.datetime.now()
    current_time = home_unit.round_to(current_time, timeunit)

    if timeunit == timeunit_old:
        s = flask.request.args.get("page", default=None)
        if s:
            return datetime.datetime.fromisoformat(s)
        else:
            return current_time
    else:
        return current_time

def get_tags() -> typing.List[orm_feeds.Tag]:
    user = flask_security.current_user

    tags_name = flask.request.args.getlist("tag")

    q = sqla.select(
        orm_feeds.Tag,
    ).where(
        orm_feeds.Tag.UserID == user.UserID,
        orm_feeds.Tag.Name.in_(tags_name),
    )

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]

def get_timeunit(old: bool=False):
    if old:
        k = "timeunit"
        v = home_unit.UnitMode.DAY.name
    else:
        k = "timeunit_new"
        v = get_timeunit(old=True).name

    unit_name = flask.request.args.get(k, default = v)
    return home_unit.UnitMode[unit_name]

def base_context():
    user = flask_security.current_user
    context = dict()

    # topnav.html.
    context["feed"] = get_wall()
    context["timeunit"] = get_timeunit()
    context["page"] = get_page()
    context["prev_page"] = home_unit.decrement_to(get_page(), get_timeunit())
    context["next_page"] = home_unit.increment_to(get_page(), get_timeunit())
    context["langs"] = get_langs()
    context["tags"] = get_tags()

    # sidenav.html.
    context["langs_disp"] = overview_db.all_langs(user)
    context["tags_disp"] = feed_db.all_tags(user, display=True)

    # sidenav.html.
    context["feeds_all"]=tag_db.all_feeds()
    context["tags_all"]=feed_db.all_tags(user)

    # sidenav.html.
    dir_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "clf.d",
        str(user.UserID)
    ))
    context["magic_exists"] = os.path.isdir(dir_path)

    # sidenav.html.
    context["enum_feed"] = home_wall.WallMode
    context["enum_timeunit"] = home_unit.UnitMode

    return context

