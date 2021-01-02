#!/usr/bin/env python3

from flask import Blueprint, request, render_template
from flask_security import auth_required

from .req import base_context
from model.utils.data import all_feeds_lang_tag
from model.utils.one import get_tag_name

bp = Blueprint("tag", __name__, url_prefix="/tag")

@bp.route("")
@auth_required()
def tag():
    tag_id = request.args.get('tag')
    tag_name = get_tag_name(tag_id)

    return render_template("tag.html",
            **base_context(),
            topnav_title=tag_name,
            feeds_lang=all_feeds_lang_tag(tag_id)
    )
