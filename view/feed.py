#!/usr/bin/env python3

from flask import Blueprint, request, render_template, redirect, url_for
from flask_security import auth_required, current_user

from .req import base_context
from model import get_session
from model.orm.feeds import Feed
from model.schema.feeds import Language
from model.utils.custom import upsert_feed, upsert_display
from model.utils.custom import delete_tags_tagged, insert_tags_untagged
from model.utils.data import all_tags_feed

bp = Blueprint("feed", __name__, url_prefix="/feed")

@bp.route("")
@auth_required()
def feed(feed_id=None):
    if not feed_id:
        feed_id = request.args.get('feed_id', type=int)
    with get_session() as session:
        feed_row = session.get(Feed, feed_id)
        feed_row.Displayed = any([user_it.UserID == current_user.UserID for user_it in feed_row.users])

    return render_template("feed.html",
            **base_context(),
            topnav_title=feed_row.Title,
            feed_row=feed_row,
            langs_all=[e for e in Language],
            lang_default=Language.ENGLISH,
            tags_feed=all_tags_feed(current_user.UserID, feed_id)
    )

@bp.route("/update_feed", methods=['POST'])
@auth_required()
def update_feed():
    feed_id = request.form.get('feed', type=int)
    title = request.form.get('title')
    link = request.form.get('link')
    lang = Language[request.form.get('lang')]
    display = request.form.get('display', type=int)

    upsert_feed(feed_id, title, link, lang)
    upsert_display(current_user.UserID, [feed_id], display)

    return redirect(url_for("feed.feed", feed_id=feed_id))

@bp.route("/toggle_tags", methods=['POST'])
@auth_required()
def toggle_tags():
    feed_id = request.form.get('feed_id', type=int)
    tagged = request.form.getlist('tagged', type=int)
    untagged = request.form.getlist('untagged', type=int)

    delete_tags_tagged(feed_id, tagged)
    insert_tags_untagged(feed_id, untagged)

    return ("", 200)
