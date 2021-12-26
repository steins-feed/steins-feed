#!/usr/bin/env python3

import flask
import flask_security
import sqlalchemy as sqla

import model
from model.orm import feeds as orm_feeds

from . import db
from .. import req

bp = flask.Blueprint("tag", __name__, url_prefix="/tag")

@bp.route("")
@flask_security.auth_required()
def tag() -> flask.Response:
    tag_id = flask.request.args.get('tag', type=int)
    with model.get_session() as session:
        tag = session.get(orm_feeds.Tag, tag_id)

    return flask.render_template(
        "tag.html",
        **req.base_context(),
        topnav_title = tag.Name,
        tag_row = tag,
        feeds_lang = db.feeds_lang(tag),
        feeds_lang_not = db.feeds_lang(tag, False),
    )

@bp.route("/toggle_feeds", methods=['POST'])
@flask_security.auth_required()
def toggle_feeds() -> flask.Response:
    tag_id = flask.request.form.get('tag_id', type=int)
    tagged = flask.request.form.getlist('tagged', type=int)
    untagged = flask.request.form.getlist('untagged', type=int)

    with model.get_session() as session:
        tag = session.get(orm_feeds.Tag, tag_id)
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

    db.delete_feeds_tagged(tag, tagged)
    db.insert_feeds_untagged(tag, untagged)

    return "", 200

