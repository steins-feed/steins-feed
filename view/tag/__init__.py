#!/usr/bin/env python3

import flask
import flask_security
import sqlalchemy as sqla

import model
from model.orm import feeds as orm_feeds

from . import db
from .. import context
from ..overview import db as overview_db
from ..tag import db as tag_db

bp = flask.Blueprint("tag", __name__, url_prefix="/tag")

@bp.route("")
@flask_security.auth_required()
def tag() -> flask.Response:
    tag_id = flask.request.args.get('tag', type=int)
    with model.get_session() as session:
        tag = session.get(orm_feeds.Tag, tag_id)

    feeds_lang = {}
    feeds_lang_not = {}

    for lang_it in overview_db.all_langs():
        feeds_lang[lang_it] = tag_db.all_feeds(
            langs=[lang_it],
            tags=[tag],
        )
        feeds_lang_not[lang_it] = tag_db.all_feeds(
            langs=[lang_it],
            tags=[tag],
            tags_flag=False,
        )

    return flask.render_template(
        "tag.html",
        **context.base_context(),
        topnav_title = tag.Name,
        tag_row = tag,
        feeds_lang = feeds_lang,
        feeds_lang_not = feeds_lang_not,
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

    db.untag_feeds(tag, *tagged)
    db.tag_feeds(tag, *untagged)

    return "", 200

