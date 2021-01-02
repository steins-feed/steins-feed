#!/usr/bin/env python3

from datetime import datetime, timedelta
from flask import Blueprint, request, render_template
from flask_security import auth_required, current_user
from lxml import etree, html

from .req import get_langs, get_page, get_tags, get_timeunit
from .req import Timeunit
from .req import base_context
from model.schema import Like
from model.utils.all import updated_dates, updated_items
from model.utils.recent import last_updated
from model.utils.score import upsert_like

bp = Blueprint("home", __name__, url_prefix="/home")

@bp.route("")
@auth_required()
def home():
    r_page = get_page()
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

    page_dates = updated_dates(current_user.UserID, date_keys, last_hour, r_page + 2)
    if len(page_dates) == r_page + 2:
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
    page_items = updated_items(current_user.UserID, get_langs(), get_tags(), start_time, finish_time, last_hour)

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
    upsert_like(current_user.UserID, int(request.form.get('id')), like_val)
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
    except etree.ParserError as e:
        return ""

    # Strip tag and content.
    tags = ['figure', 'img', 'iframe', 'script', 'small', 'svg']
    for tag_it in tags:
        elems = tree.xpath("//{}".format(tag_it))
        for elem_it in elems:
            elem_it.drop_tree()

    # Strip class and content.
    classes = ['twitter']
    for class_it in classes:
        elems = tree.xpath("//*[contains(@class, '" + class_it + "')]")
        for elem_it in reversed(elems):
            elem_it.drop_tree()

    # Remove leading and trailing tags.
    tags = ['br']
    #while (true) {
    #    if (!is_null($tree_body->firstChild) and in_array($tree_body->firstChild->tagName, $tags)) {
    #        $tree_body->removeChild($tree_body->firstChild);
    #    } else {
    #        break;
    #    }
    #}
    #while (true) {
    #    if (!is_null($tree_body->lastChild) and in_array($tree_body->lastChild->tagName, $tags)) {
    #        $tree_body->removeChild($tree_body->lastChild);
    #    } else {
    #        break;
    #    }
    #}

    # Strip tag.
    tags = ['em', 'hr', 'strong']
    for tag_it in tags:
        elems = tree.xpath("//{}".format(tag_it))
        for elem_it in elems:
            elem_it.drop_tag()

    # Replace tag.
    tags = ['h1', 'h2'];
    for tag_it in tags:
        elems = tree.xpath("//{}".format(tag_it))
        for elem_it in elems:
            elem_it.tag = 'h3'

    # Strip empty tags.
    tags = ['div', 'p', 'span']
    empty_leaves(tree, tags)

    return html.tostring(tree).decode()

def empty_leaves(e, tags=[]):
    for e_it in reversed(list(e)):
        empty_leaves(e_it)

    if not len(e) and not e.text and (not len(tags) or e.tag in tags):
        e.drop_tree()