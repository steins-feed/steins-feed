#!/usr/bin/env python3

import flask_security
import typing

from magic import io as magic_io
from model.orm import users as orm_users
from view.feed import db as feed_db
from view.home import unit as home_unit
from view.home import wall as home_wall
from view.overview import db as overview_db
from view.tag import db as tag_db

from . import req

def base_context():
    user = flask_security.current_user

    context = dict()
    context.update(topnav_context())
    context.update(sidenav_context(user))

    return context

def topnav_context() -> typing.Dict[str, typing.Any]:
    context = {}

    context["feed"] = req.get_wall()
    context["langs"] = req.get_langs()
    context["tags"] = req.get_tags()
    context["timeunit"] = req.get_timeunit()

    context["page"] = req.get_page()
    context["prev_page"] = home_unit.decrement_to(
        context["page"],
        context["timeunit"],
    )
    context["next_page"] = home_unit.increment_to(
        context["page"],
        context["timeunit"],
    )

    return context

def sidenav_context(
    user: orm_users.User,
) -> typing.Dict[str, typing.Any]:
    context = {}

    context["langs_disp"] = overview_db.all_langs(user)
    context["tags_disp"] = feed_db.all_tags(user, display=True)

    context["feeds_all"]=tag_db.all_feeds()
    context["tags_all"]=feed_db.all_tags(user)

    context["magic_exists"] = magic_io.magic_exists(user)

    context["enum_feed"] = home_wall.WallMode
    context["enum_timeunit"] = home_unit.UnitMode

    return context

