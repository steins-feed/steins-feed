#!/usr/bin/env python3

from datetime import datetime, timedelta
from html import unescape
from lxml import etree, html
import os

from flask import Blueprint, request, render_template, redirect, url_for
from flask_security import auth_required, current_user
import sqlalchemy as sqla

import magic
from magic.io import trained_languages
from model.recent import last_updated
from model.schema.items import Like

from . import db
from ..req import get_feed, get_langs, get_page, get_tags, get_timeunit
from ..req import Feed, Timeunit
from ..req import base_context

bp = Blueprint("home", __name__, url_prefix="/home")

@bp.route("")
@auth_required()
def home():
    r_feed = get_feed()
    r_langs = get_langs()
    r_page = get_page()
    r_tags = get_tags()
    r_timeunit = get_timeunit()

    last_hour = last_updated().replace(
            minute=0, second=0, microsecond=0
    )
    if r_timeunit == Timeunit.DAY:
        date_keys = ["Year", "Month", "Day"]
    elif r_timeunit == Timeunit.WEEK:
        date_keys = ["Year", "Week"]
    elif r_timeunit == Timeunit.MONTH:
        date_keys = ["Year", "Month"]
    else:
        raise ValueError

    page_dates = db.updated_dates(current_user.UserID, date_keys, last_hour, r_page + 2)
    if len(page_dates) == 0:
        return redirect(url_for("overview.settings"))
    elif len(page_dates) == r_page + 2:
        page_date = page_dates[-2]
    else:
        page_date = page_dates[-1]

    start_time = page_date
    finish_time = start_time
    if r_timeunit == Timeunit.DAY:
        finish_time += timedelta(days=1)
    elif r_timeunit == Timeunit.WEEK:
        finish_time += timedelta(days=7)
    elif r_timeunit == Timeunit.MONTH:
        finish_time += timedelta(days=31)
        finish_time = finish_time.replace(day=1)
    else:
        raise ValueError

    if r_feed == Feed.MAGIC:
        for lang_it in trained_languages(current_user):
            new_items = db.unscored_items(
                current_user.UserID,
                lang_it,
                r_tags,
                start_time,
                finish_time,
                last_hour
            )
            if len(new_items) == 0:
                continue

            new_scores = magic.compute_score(current_user.UserID, lang_it, new_items)
            db.upsert_magic(current_user.UserID, new_items, new_scores)

    page_items = db.updated_items(
        current_user.UserID,
        r_langs,
        r_tags,
        start_time,
        finish_time,
        last_hour,
        r_feed == Feed.MAGIC
    )

    return render_template("index.html",
            **base_context(),
            topnav_title=get_topnav_title(page_date, r_timeunit),
            last_updated=last_hour,
            dates=page_dates,
            items=page_items,
            enum_like=Like
    )

@bp.route("/like", methods=['POST'])
@auth_required()
def like(like_val = Like.UP):
    db.upsert_like(current_user.UserID, int(request.form.get('id')), like_val)
    return ("", 200)

@bp.route("/dislike", methods=['POST'])
@auth_required()
def dislike():
    return like(Like.DOWN)

def get_topnav_title(page_date, timeunit):
    current_date = datetime.now()
    if timeunit == Timeunit.DAY:
        if current_date >= page_date and current_date < page_date + timedelta(days=1):
            topnav_title = "Today"
        elif current_date - timedelta(days=1) >= page_date and current_date - timedelta(days=1) < page_date + timedelta(days=1):
            topnav_title = "Yesterday"
        else:
            topnav_title = page_date.strftime("%a, %d %b %Y")
    elif timeunit == timeunit.WEEK:
        if current_date >= page_date and current_date < page_date + timedelta(days=7):
            topnav_title = "This week"
        elif current_date - timedelta(days=7) >= page_date and current_date - timedelta(days=7) < page_date + timedelta(days=7):
            topnav_title = "Last week"
        else:
            topnav_title = page_date.strftime("Week %U, %Y")
    elif timeunit == timeunit.MONTH:
        if current_date >= page_date and current_date < (page_date + timedelta(days=31)).replace(day=1):
            topnav_title = "This month"
        elif (current_date - timedelta(days=31)).replace(day=1) >= page_date and (current_date - timedelta(days=31)).replace(day=1) < (page_date + timedelta(days=31)).replace(day=1):
            topnav_title = "Last month"
        else:
            topnav_title = page_date.strftime("%B %Y")
    else:
        raise ValueError

    return topnav_title

def clean_summary(s):
    try:
        tree = html.fromstring(s)
    except etree.ParserError:
        return ""
    except etree.XMLSyntaxError:
        return ""

    # Penalize if full document.
    tags = ['h' + str(e + 1) for e in range(6)];
    for tag_it in tags:
        elems = tree.xpath("//{}".format(tag_it))
        if len(elems) > 0:
            return ""

    # Strip tags and content.
    tags = ['figure', 'img']
    if tree.tag in tags:
        return ""
    etree.strip_elements(tree, *tags, with_tail=False)

    # Strip classes and content.
    classes = ['instagram', 'tiktok', 'twitter']
    for class_it in classes:
        elems = tree.xpath("//*[contains(@class, '" + class_it + "')]")
        for elem_it in reversed(elems):
            elem_it.drop_tree()

    # Strip empty tags.
    tags = ['div', 'p', 'span']
    empty_leaves(tree, tags)

    return unescape(html.tostring(tree, encoding='unicode', method='html'))

def empty_leaves(e, tags=[]):
    for e_it in reversed(list(e)):
        empty_leaves(e_it)

    if len(e) == 0 and not e.text and not e.tail and (len(tags) == 0 or e.tag in tags):
        e.drop_tree()

