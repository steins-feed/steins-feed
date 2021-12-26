#!/usr/bin/env python3

from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import auth_required, current_user
import sqlalchemy as sqla

from model import get_session
from model.orm.feeds import Feed
from model.orm.items import Item, Like
from model.orm.users import User
from model.schema.feeds import Language
from model.schema.items import Like as LikeEnum
from model.utils import all_langs_feeds
from model.utils.custom import delete_feeds
from model.utils.custom import upsert_tag, delete_tags

from .req import base_context
from .feed.db import upsert_feed, upsert_display

bp = Blueprint("overview", __name__)

@bp.route("/statistics")
@auth_required()
def statistics():
    return render_template("statistics.html",
            **base_context(),
            topnav_title=current_user.Name,
            likes_lang=likes_lang(current_user.UserID),
            dislikes_lang=likes_lang(current_user.UserID, LikeEnum.DOWN.name),
    )

@bp.route("/settings")
@auth_required()
def settings():
    return render_template("settings.html",
            **base_context(),
            topnav_title=current_user.Name,
            langs_all=[e for e in Language],
            lang_default=Language.ENGLISH,
            feeds_lang=feeds_lang_disp(current_user.UserID),
            feeds_lang_not=feeds_lang_disp(current_user.UserID, False),
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

def likes_lang(user_id, score=LikeEnum.UP.name):
    q = sqla.select(
        Item
    ).join(
        Item.feed
    ).join(
        Item.likes.and_(
            Like.UserID == user_id,
        )
    ).where(
        Like.Score == score,
        Feed.Language == sqla.bindparam("lang"),
    ).order_by(
        sqla.desc(Item.Published),
    ).options(
        sqla.orm.contains_eager(Item.feed),
    )

    res = dict()
    with get_session() as session:
        for lang_it in all_langs_feeds():
            lang_it = Language(lang_it)
            res[lang_it] = [
                e[0] for e in session.execute(q, {"lang": lang_it.name})
            ]

    return res

def feeds_lang_disp(user_id, flag=True):
    res = dict()

    for lang_it in all_langs_feeds():
        lang_it = Language(lang_it)

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
