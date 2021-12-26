#!/usr/bin/env python3

from datetime import timedelta

from flask import Blueprint, request, render_template
from flask_security import auth_required, current_user
import sqlalchemy as sqla

import magic
from magic import io as magic_io
from model import recent
from model.schema import items as schema_items

from . import db
from . import util
from .. import req

bp = Blueprint("home", __name__, url_prefix="/home")
bp.add_app_template_filter(util.clean_summary, "clean")

@bp.route("")
@auth_required()
def home():
    r_feed = req.get_feed()
    r_langs = req.get_langs()
    r_page = req.get_page()
    r_tags = req.get_tags()
    r_timeunit = req.get_timeunit()

    last_hour = recent.last_updated()
    last_hour = last_hour.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    start_time = r_page
    finish_time = start_time
    if r_timeunit == req.Timeunit.DAY:
        finish_time += timedelta(days=1)
    elif r_timeunit == req.Timeunit.WEEK:
        finish_time += timedelta(days=7)
    elif r_timeunit == req.Timeunit.MONTH:
        finish_time += timedelta(days=31)
        finish_time = finish_time.replace(day=1)
    else:
        raise ValueError

    if r_feed == req.Feed.MAGIC:
        for lang_it in magic_io.trained_languages(current_user):
            new_items = db.unscored_items(
                current_user.UserID,
                lang_it,
                r_tags,
                start_time,
                finish_time,
                last_hour,
            )
            if len(new_items) == 0:
                continue

            new_scores = magic.compute_score(current_user.UserID, lang_it, new_items)
            db.upsert_magic(current_user.UserID, new_items, new_scores)

    page_items = db.updated_items(
        current_user.UserID,
        r_langs,
        r_tags,
        start_time,
        finish_time,
        last_hour,
        r_feed == req.Feed.MAGIC,
    )

    return render_template("index.html",
            **req.base_context(),
            topnav_title=util.format_date(r_page, r_timeunit),
            last_updated=last_hour,
            items=page_items,
            enum_like=schema_items.Like
    )

@bp.route("/like", methods=['POST'])
@auth_required()
def like(like_val = schema_items.Like.UP):
    db.upsert_like(current_user.UserID, int(request.form.get('id')), like_val)
    return ("", 200)

@bp.route("/dislike", methods=['POST'])
@auth_required()
def dislike():
    return like(schema_items.Like.DOWN)

