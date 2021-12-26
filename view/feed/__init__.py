#!/usr/bin/env python3

import flask
import flask_security
import sqlalchemy as sqla

import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds
from model.utils.custom import upsert_feed, upsert_display
from model.utils.custom import delete_tags_tagged, insert_tags_untagged

from ..req import base_context

bp = flask.Blueprint("feed", __name__, url_prefix="/feed")

@bp.route("")
@flask_security.auth_required()
def feed(feed_id=None):
    if not feed_id:
        feed_id = flask.request.args.get("feed_id", type=int)

    user = flask_security.current_user

    with model.get_session() as session:
        feed_row = session.get(
            orm_feeds.Feed,
            feed_id,
            options=[
                sqla.orm.selectinload(orm_feeds.Feed.users.and_(
                    orm_users.User.UserID == user.UserID,
                )),
            ],
        )

    return flask.render_template("feed.html",
        **base_context(),
        topnav_title=feed_row.Title,
        feed_row=feed_row,
        langs_all=[e for e in schema_feeds.Language],
        lang_default=schema_feeds.Language.ENGLISH,
        feed_tags=feed_tags(user.UserID, feed_id),
        feed_tags_not=feed_tags(user.UserID, feed_id, False),
    )

@bp.route("/update_feed", methods=["POST"])
@flask_security.auth_required()
def update_feed():
    feed_id = flask.request.form.get("feed", type=int)
    title = flask.request.form.get("title")
    link = flask.request.form.get("link")
    lang = schema_feeds.Language[flask.request.form.get("lang")]
    display = flask.request.form.get("display", type=int)

    user = flask_security.current_user

    upsert_feed(feed_id, title, link, lang)
    upsert_display(user.UserID, [feed_id], display)

    return flask.redirect(flask.url_for("feed.feed", feed_id=feed_id))

@bp.route("/toggle_tags", methods=["POST"])
@flask_security.auth_required()
def toggle_tags():
    feed_id = flask.request.form.get("feed_id", type=int)
    tagged = flask.request.form.getlist("tagged", type=int)
    untagged = flask.request.form.getlist("untagged", type=int)

    delete_tags_tagged(feed_id, tagged)
    insert_tags_untagged(feed_id, untagged)

    return ("", 200)

def feed_tags(user_id, feed_id, flag=True):
    q = sqla.select(
        orm_feeds.Tag
    ).where(
        orm_feeds.Tag.UserID == user_id
    ).order_by(
        sqla.collate(orm_feeds.Tag.Name, "NOCASE")
    )
    if flag:
        q = q.where(orm_feeds.Tag.feeds.any(orm_feeds.Feed.FeedID == feed_id))
    else:
        q = q.where(~orm_feeds.Tag.feeds.any(orm_feeds.Feed.FeedID == feed_id))

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]
