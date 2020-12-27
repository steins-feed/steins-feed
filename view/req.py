#!/usr/bin/env python3

from enum import Enum
from flask import request
from flask_security import current_user

from model.utils.all import all_feeds, all_tags
from model.utils.all import displayed_languages, displayed_tags

class Feed(Enum):
    FULL = "Full"
    MAGIC = "Magic"
    SURPRISE = "Surprise"

class Timeunit(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

def get_feed():
    return request.args.get('feed', default=Feed.FULL, type=Feed)

def get_langs():
    return request.args.getlist('lang')

def get_page():
    return request.args.get('page', default=0, type=int)

def get_tags():
    return request.args.getlist('tag')

def get_timeunit():
    return request.args.get('timeunit', default=Timeunit.DAY, type=Timeunit)

def base_context():
    context = dict()

    context['feed'] = get_feed()
    context['timeunit'] = get_timeunit()
    context['page'] = get_page()
    context['langs'] = get_langs()
    context['tags'] = get_tags()

    context['langs_disp'] = displayed_languages(current_user.UserID)
    context['tags_disp'] = displayed_tags(current_user.UserID)

    context['feeds_all']=all_feeds()
    context['tags_all']=all_tags(current_user.UserID)

    return context
