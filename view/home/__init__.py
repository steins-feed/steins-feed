#!/usr/bin/env python3

import flask
import flask_security

import magic
from magic import io as magic_io
import model
from model import recent
from model.orm import items as orm_items
from model.schema import items as schema_items

from . import db
from . import util
from . import unit
from . import wall
from .. import req

bp = flask.Blueprint("home", __name__, url_prefix="/home")
bp.add_app_template_filter(util.clean_summary, "clean")

@bp.route("")
@flask_security.auth_required()
def home():
    r_wall = req.get_wall()
    r_langs = req.get_langs()
    r_page = req.get_page()
    r_tags = req.get_tags()
    r_timeunit = req.get_timeunit()

    user = flask_security.current_user
    last_hour = recent.last_updated()
    last_hour = last_hour.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    start_time = r_page
    finish_time = unit.increment_to(start_time, r_timeunit)

    if r_wall == wall.WallMode.MAGIC:
        for lang_it in magic_io.trained_languages(user):
            new_items = db.unscored_items(
                user,
                lang_it,
                r_tags,
                start_time,
                finish_time,
                last_hour,
            )
            if len(new_items) == 0:
                continue

            new_scores = magic.compute_score(user.UserID, lang_it, new_items)
            db.upsert_magic(user, new_items, new_scores)

    page_items = db.updated_items(
        user,
        r_langs,
        r_tags,
        start_time,
        finish_time,
        last_hour,
        r_wall,
    )

    return flask.render_template(
        "index.html",
        **req.base_context(),
        topnav_title = unit.format_to(r_page, r_timeunit),
        last_updated = last_hour,
        items = page_items,
        enum_like = schema_items.Like,
    )

@bp.route("/like", methods=["POST"])
@flask_security.auth_required()
def like(
    like_val: schema_items.Like = schema_items.Like.UP,
) -> flask.Response:
    user = flask_security.current_user
    item_id = flask.request.form.get("id", type=int)
    with model.get_session() as session:
        item = session.get(orm_items.Item, item_id)

    db.upsert_like(user, item, like_val)

    return "", 200

@bp.route("/dislike", methods=["POST"])
@flask_security.auth_required()
def dislike() -> flask.Response:
    return like(schema_items.Like.DOWN)

