#!/usr/bin/env python3

import flask
import flask_security

import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from model.schema import items as schema_items
from model.utils.custom import upsert_tag, delete_tags

from . import db
from .. import req
from ..feed import db as feed_db

bp = flask.Blueprint("overview", __name__)

@bp.route("/statistics")
@flask_security.auth_required()
def statistics() -> flask.Response:
    user = flask_security.current_user

    return flask.render_template(
        "statistics.html",
        **req.base_context(),
        topnav_title = user.Name,
        likes_lang = db.likes_lang(user),
        dislikes_lang = db.likes_lang(user, schema_items.Like.DOWN),
    )

@bp.route("/settings")
@flask_security.auth_required()
def settings() -> flask.Response:
    user = flask_security.current_user

    return flask.render_template("settings.html",
            **req.base_context(),
            topnav_title = user.Name,
            langs_all = schema_feeds.Language,
            lang_default = schema_feeds.Language.ENGLISH,
            feeds_lang = db.feeds_lang_disp(user),
            feeds_lang_not = db.feeds_lang_disp(user, False),
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
def add_tag():
    user = flask_security.current_user
    upsert_tag(None, user.UserID, flask.request.form.get("tag"))
    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/delete_tag", methods=["POST"])
@flask_security.auth_required()
def delete_tag():
    delete_tags([flask.request.form.get("tag", type=int)])
    return flask.redirect(flask.url_for("overview.settings"))

