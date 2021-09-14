#!/usr/bin/env python3

from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import auth_required, current_user

from .req import base_context
from model.schema.feeds import Language
from model.utils.custom import upsert_feed, upsert_display, delete_feeds
from model.utils.custom import upsert_tag, delete_tags
from model.utils.data import all_feeds_lang_disp, all_likes_lang

bp = Blueprint("overview", __name__)

@bp.route("/statistics")
@auth_required()
def statistics():
    return render_template("statistics.html",
            **base_context(),
            topnav_title=current_user.Name,
            likes_lang=all_likes_lang(current_user.UserID)
    )

@bp.route("/settings")
@auth_required()
def settings():
    return render_template("settings.html",
            **base_context(),
            topnav_title=current_user.Name,
            langs_all=[e for e in Language],
            lang_default=Language.ENGLISH,
            feeds_lang=all_feeds_lang_disp(current_user.UserID)
    )

@bp.route("/settings/toggle_display", methods=['POST'])
@auth_required()
def toggle_display():
    tagged = request.form.getlist('displayed', type=int)
    untagged = request.form.getlist('hidden', type=int)

    if tagged:
        upsert_display(current_user.UserID, tagged, 0)
    if untagged:
        upsert_display(current_user.UserID, untagged, 1)

    return ("", 200)

@bp.route("/settings/add_feed", methods=['POST'])
@auth_required()
def add_feed():
    title = request.form.get('title')
    link = request.form.get('link')
    lang = Language[request.form.get('lang')]

    feed_id = upsert_feed(None, title, link, lang)
    upsert_display(current_user.UserID, [feed_id], 1)

    return redirect(url_for("overview.settings"))

@bp.route("/settings/delete_feed", methods=['POST'])
@auth_required()
def delete_feed():
    delete_feeds([request.form.get('feed', type=int)])
    return redirect(url_for("overview.settings"))

@bp.route("/settings/add_tag", methods=['POST'])
@auth_required()
def add_tag():
    upsert_tag(None, current_user.UserID, request.form.get('tag'))
    return redirect(url_for("overview.settings"))

@bp.route("/settings/delete_tag", methods=['POST'])
@auth_required()
def delete_tag():
    delete_tags([request.form.get('tag', type=int)])
    return redirect(url_for("overview.settings"))
