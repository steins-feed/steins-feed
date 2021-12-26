#!/usr/bin/env python3

import flask
import flask_security
import sqlalchemy as sqla

from model import get_session
from model.orm.feeds import Feed
from model.orm.users import User
from model.schema import feeds as schema_feeds
from model.schema import items as schema_items
from model.utils import all_langs_feeds
from model.utils.custom import delete_feeds
from model.utils.custom import upsert_tag, delete_tags

from . import db
from ..req import base_context

bp = flask.Blueprint("overview", __name__)

@bp.route("/statistics")
@flask_security.auth_required()
def statistics():
    user = flask_security.current_user

    return flask.render_template(
        "statistics.html",
        **base_context(),
        topnav_title = user.Name,
        likes_lang = db.likes_lang(user),
        dislikes_lang = db.likes_lang(user, schema_items.Like.DOWN),
    )

@bp.route("/settings")
@flask_security.auth_required()
def settings():
    user = flask_security.current_user

    return flask.render_template("settings.html",
            **base_context(),
            topnav_title=user.Name,
            langs_all=schema_feeds.Language,
            lang_default=schema_feeds.Language.ENGLISH,
            feeds_lang=feeds_lang_disp(user.UserID),
            feeds_lang_not=feeds_lang_disp(user.UserID, False),
    )

@bp.route("/settings/toggle_display", methods=['POST'])
@flask_security.auth_required()
def toggle_display():
    user = flask_security.current_user
    tagged = flask.request.form.getlist('displayed', type=int)
    untagged = flask.request.form.getlist('hidden', type=int)

    if tagged:
        upsert_display(user.UserID, tagged, 0)
    if untagged:
        upsert_display(user.UserID, untagged, 1)

    return ("", 200)

@bp.route("/settings/add_feed", methods=['POST'])
@flask_security.auth_required()
def add_feed():
    user = flask_security.current_user

    title = flask.request.form.get('title')
    link = flask.request.form.get('link')
    lang = schema_feeds.Language[flask.request.form.get('lang')]

    feed_id = upsert_feed(None, title, link, lang)
    upsert_display(user.UserID, [feed_id], 1)

    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/delete_feed", methods=['POST'])
@flask_security.auth_required()
def delete_feed():
    delete_feeds([flask.request.form.get('feed', type=int)])
    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/add_tag", methods=['POST'])
@flask_security.auth_required()
def add_tag():
    user = flask_security.current_user
    upsert_tag(None, user.UserID, flask.request.form.get('tag'))
    return flask.redirect(flask.url_for("overview.settings"))

@bp.route("/settings/delete_tag", methods=['POST'])
@flask_security.auth_required()
def delete_tag():
    delete_tags([flask.request.form.get('tag', type=int)])
    return flask.redirect(flask.url_for("overview.settings"))

def feeds_lang_disp(user_id, flag=True):
    res = dict()

    for lang_it in all_langs_feeds():
        q = sqla.select(
            Feed
        ).where(
            Feed.Language == lang_it.name
        ).order_by(
            sqla.collate(Feed.Title, 'NOCASE')
        )
        if flag:
            q = q.where(Feed.users.any(User.UserID == user_id))
        else:
            q = q.where(~Feed.users.any(User.UserID == user_id))

        with get_session() as session:
            res[lang_it] = [e[0] for e in session.execute(q)]

    return res

