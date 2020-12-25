#!/usr/bin/env python3

from enum import Enum
from flask import request

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
