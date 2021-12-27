#!/usr/bin/env python3

import flask
import flask_security

import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from model.schema import items as schema_items

from . import db
from .. import context
from ..feed import db as feed_db
from ..tag import db as tag_db

bp = flask.Blueprint("overview", __name__)

@bp.route("/statistics")
@flask_security.auth_required()
def statistics() -> flask.Response:
    user = flask_security.current_user

    likes_lang = {}
    dislikes_lang = {}

    for lang_it in db.all_langs():
        likes_lang[lang_it] = db.all_likes(
            user,
            lang_it,
        )
        dislikes_lang[lang_it] = db.all_likes(
            user,
            lang_it,
            schema_items.Like.DOWN,
        )

    return flask.render_template(
        "statistics.html",
        **context.base_context(),
        topnav_title = user.Name,
        likes_lang = likes_lang,
        dislikes_lang = dislikes_lang,
    )

@bp.route("/settings")
@flask_security.auth_required()
def settings() -> flask.Response:
    user = flask_security.current_user

    feeds_lang = {}
    feeds_lang_not = {}

    for lang_it in db.all_langs():
        feeds_lang[lang_it] = tag_db.all_feeds(
            langs = [lang_it],
            users = [user],
        )
        feeds_lang_not[lang_it] = tag_db.all_feeds(
            langs = [lang_it],
            users = [user],
            users_flag = False,
        )

    return flask.render_template("settings.html",
            **context.base_context(),
            topnav_title = user.Name,
            langs_all = schema_feeds.Language,
            lang_default = schema_feeds.Language.ENGLISH,
            feeds_lang = feeds_lang,
            feeds_lang_not = feeds_lang_not,
    )

@bp.route("/settings/toggle_display", methods=["POST"])
@flask_security.auth_required()
def toggle_display() -> flask.Response:
    user = flask_security.current_user
    tagged = flask.request.form.getlist("displayed", type=int)
    untagged = flask.request.form.getlist("hidden", type=int)

    with model.get_session() as session:
        tagged = [
            session.get(
                orm_feeds.Feed,
                feed_id,
            ) for feed_id in tagged
        ]
        untagged = [
            session.get(
                orm_feeds.Feed,
                feed_id,
            ) for feed_id in untagged
        ]

    if tagged:
        feed_db.upsert_display(user, *tagged, displayed=False)
    if untagged:
        feed_db.upsert_display(user, *untagged, displayed=True)

    return "", 200

@bp.route("/settings/add_feed", methods=["POST"])
@flask_security.auth_required()
def add_feed() -> flask.Response:
    user = flask_security.current_user

    title = flask.request.form.get("title")
    link = flask.request.form.get("link")
    lang = schema_feeds.Language[flask.request.form.get("lang")]

    feed = feed_db.insert_feed(title, link, lang)
    feed_db.upsert_display(user, feed, displayed=True)

    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/delete_feed", methods=["POST"])
@flask_security.auth_required()
def delete_feed() -> flask.Response:
    feed_id = flask.request.form.get("feed", type=int)
    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed_id,
        )

    feed_db.delete_feeds(feed)

    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/add_tag", methods=["POST"])
@flask_security.auth_required()
def add_tag() -> flask.Response:
    user = flask_security.current_user
    tag_name = flask.request.form.get("tag")
    tag_db.insert_tag(user, tag_name)

    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/delete_tag", methods=["POST"])
@flask_security.auth_required()
def delete_tag() -> flask.Response:
    tag_id = flask.request.form.get("tag", type=int)
    with model.get_session() as session:
        tag = session.get(
            orm_feeds.Tag,
            tag_id,
        )

    tag_db.delete_tags(tag)

    return flask.redirect(flask.url_for("overview.settings"))

