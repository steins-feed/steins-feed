#!/usr/bin/env python3

from flask import Blueprint, request, render_template
from flask_security import auth_required
import sqlalchemy as sqla

from model import get_session
from model.orm.feeds import Feed, Tag
from model.schema.feeds import Language
from model.utils.custom import delete_feeds_tagged, insert_feeds_untagged

from . import db
from ..req import base_context

bp = Blueprint("tag", __name__, url_prefix="/tag")

@bp.route("")
@auth_required()
def tag():
    tag_id = request.args.get('tag', type=int)
    with get_session() as session:
        tag_row = session.get(Tag, tag_id)

    return render_template("tag.html",
            **base_context(),
            topnav_title=tag_row.Name,
            tag_row=tag_row,
            feeds_lang=db.feeds_lang(tag_id),
            feeds_lang_not=db.feeds_lang(tag_id, False),
    )

@bp.route("/toggle_feeds", methods=['POST'])
@auth_required()
def toggle_feeds():
    tag_id = request.form.get('tag_id', type=int)
    tagged = request.form.getlist('tagged', type=int)
    untagged = request.form.getlist('untagged', type=int)

    delete_feeds_tagged(tag_id, tagged)
    insert_feeds_untagged(tag_id, untagged)

    return ("", 200)

