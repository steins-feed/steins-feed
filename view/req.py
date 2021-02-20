#!/usr/bin/env python3

import enum
from flask import request
from flask_security import current_user

from model.schema import Language
from model.utils.all import all_feeds, all_tags
from model.utils.all import displayed_languages, displayed_tags

class Feed(enum.Enum):
    FULL = "Full"
    MAGIC = "Magic"
    SURPRISE = "Surprise"

class Timeunit(enum.Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

def get_feed():
    return Feed[request.args.get('feed', default=Feed.FULL.name)]

def get_langs():
    res = [Language[e] for e in request.args.getlist('lang')]
    if set(displayed_languages(current_user.UserID)) <= set(res):
        res = []
    return res

def get_page():
    if get_timeunit_new() == get_timeunit_old():
        return request.args.get('page', default=0, type=int)
    else:
        return 0

def get_tags():
    return request.args.getlist('tag')

def get_timeunit():
    return get_timeunit_new()

def get_timeunit_old():
    return Timeunit[request.args.get('timeunit', default=Timeunit.DAY.name)]

def get_timeunit_new():
    return Timeunit[request.args.get('timeunit_new', default=get_timeunit_old().name)]

def base_context():
    context = dict()

    # topnav.html.
    context['feed'] = get_feed()
    context['timeunit'] = get_timeunit()
    context['page'] = get_page()
    context['langs'] = get_langs()
    context['tags'] = get_tags()

    # sidenav.html.
    context['langs_disp'] = displayed_languages(current_user.UserID)
    context['tags_disp'] = displayed_tags(current_user.UserID)

    # sidenav.html.
    context['feeds_all']=all_feeds()
    context['tags_all']=all_tags(current_user.UserID)

    # sidenav.html.
    context['enum_feed'] = Feed
    context['enum_timeunit'] = Timeunit

    return context
