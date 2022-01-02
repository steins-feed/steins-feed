#!/usr/bin/env python3

import datetime
import flask
import flask_security
import sqlalchemy as sqla
import typing

import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from view.home import unit as home_unit
from view.home import wall as home_wall
from view.overview import db as overview_db

def get_wall() -> home_wall.WallMode:
    wall_name = flask.request.args.get(
        "wall",
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
    unit_mode = get_unit()
    unit_mode_old = get_unit(old=True)

    current_time = datetime.datetime.now()
    current_time = home_unit.round_to(current_time, unit_mode)

    if unit_mode == unit_mode_old:
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

def get_unit(
    old: bool = False,
) -> home_unit.UnitMode:
    if old:
        k = "unit"
        v = home_unit.UnitMode.DAY.name
    else:
        k = "unit_new"
        v = get_unit(old=True).name

    unit_name = flask.request.args.get(k, default=v)
    return home_unit.UnitMode[unit_name]

