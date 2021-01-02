#!/usr/bin/env python3

from flask import Blueprint, request, render_template
from flask_security import auth_required, current_user

from .req import base_context
from model.schema import Language
from model.utils.custom import delete_tags_tagged, insert_tags_untagged
from model.utils.data import all_tags_feed
from model.utils.one import get_feed_row

bp = Blueprint("feed", __name__, url_prefix="/feed")

@bp.route("")
@auth_required()
def feed():
    feed_id = request.args.get('feed_id')
    feed_row = get_feed_row(feed_id, current_user.UserID)

    return render_template("feed.html",
            **base_context(),
            topnav_title=feed_row['Title'],
            feed_row=feed_row,
            langs_all=[e for e in Language],
            lang_default=Language.ENGLISH,
            tags_feed=all_tags_feed(current_user.UserID, feed_id)
    )

@bp.route("/toggle_tags", methods=['POST'])
@auth_required()
def toggle_tags():
    feed_id = request.form.get('feed_id')
    tagged = request.form.getlist('tagged')
    untagged = request.form.getlist('untagged')

    delete_tags_tagged(feed_id, tagged)
    insert_tags_untagged(feed_id, untagged)

    return ("", 200)
