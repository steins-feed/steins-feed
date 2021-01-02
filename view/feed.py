#!/usr/bin/env python3

from flask import Blueprint, request, render_template
from flask_security import auth_required, current_user

from .req import base_context
from model.schema import Language
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
