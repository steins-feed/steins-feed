#!/usr/bin/env python3

import flask
import flask_security
import sqlalchemy as sqla

import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

from . import db
from .. import req

bp = flask.Blueprint("feed", __name__, url_prefix="/feed")

@bp.route("")
@flask_security.auth_required()
def feed(
    feed_id: int = None,
) -> flask.Response:
    if not feed_id:
        feed_id = flask.request.args.get("feed_id", type=int)

    user = flask_security.current_user

    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed_id,
            options=[
                sqla.orm.selectinload(
                    orm_feeds.Feed.users.and_(
                        orm_users.User.UserID == user.UserID,
                    )
                ),
            ],
        )

    return flask.render_template(
        "feed.html",
        **req.base_context(),
        topnav_title = feed.Title,
        feed_row = feed,
        langs_all = schema_feeds.Language,
        lang_default = schema_feeds.Language.ENGLISH,
        feed_tags = db.feed_tags(user, feed),
        feed_tags_not = db.feed_tags(user, feed, False),
    )

@bp.route("/update_feed", methods=["POST"])
@flask_security.auth_required()
def update_feed() -> flask.Response:
    feed_id = flask.request.form.get("feed", type=int)
    title = flask.request.form.get("title")
    link = flask.request.form.get("link")
    lang = schema_feeds.Language[flask.request.form.get("lang")]
    display = bool(flask.request.form.get("display", type=int))

    user = flask_security.current_user
    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed_id,
        )

    db.update_feed(feed, title, link, lang)
    db.upsert_display(user, feed, display)

    return flask.redirect(flask.url_for("feed.feed", feed_id=feed_id))

@bp.route("/toggle_tags", methods=["POST"])
@flask_security.auth_required()
def toggle_tags() -> flask.Response:
    feed_id = flask.request.form.get("feed_id", type=int)
    tagged = flask.request.form.getlist("tagged", type=int)
    untagged = flask.request.form.getlist("untagged", type=int)

    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed_id,
        )
        tagged = [
            session.get(
                orm_feeds.Tag,
                tag_id,
            ) for tag_id in tagged
        ]
        untagged = [
            session.get(
                orm_feeds.Tag,
                tag_id,
            ) for tag_id in untagged
        ]

    db.delete_tags_tagged(feed, tagged)
    db.insert_tags_untagged(feed, untagged)

    return ("", 200)

