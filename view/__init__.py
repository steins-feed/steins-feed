#!/usr/bin/env python3

from datetime import timedelta
from flask import Flask, render_template
from flask_security import auth_required, current_user
import os
import os.path as os_path

from .auth import get_security
from .req import get_feed, get_langs, get_page, get_tags, get_timeunit
from .req import Timeunit
from model.schema import Language
from model.utils import last_updated
from model.utils import updated_dates, updated_items
from model.utils import displayed_languages, displayed_tags
from model.utils import all_feeds, all_feeds_lang, all_tags, all_likes_lang

static_path = os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "static"
))
templates_path = os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "templates"
))
app = Flask(__name__,
        static_folder=static_path,
        template_folder=templates_path
)
security = get_security(app)
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.filters['contains'] = lambda a, b: set(a) >= set(b)

@app.route("/")
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
    page_dates = updated_dates(current_user.UserID, date_keys, last_hour, r_page + 2)
    if len(page_dates) == r_page + 2:
        page_date = page_dates[-2]
    else:
        page_date = page_dates[-1]

    start_time = page_date
    if r_timeunit == Timeunit.DAY:
        finish_time = start_time + timedelta(days=1)
    elif r_timeunit == Timeunit.WEEK:
        finish_time = start_time + timedelta(weeks=1)
    elif r_timeunit == Timeunit.MONTH:
        finish_time = start_time + timedelta(months=1)
    else:
        raise ValueError
    page_items = updated_items(current_user.UserID, r_langs, r_tags, start_time, finish_time, last_hour)

    return render_template("index.html",
            timeunit=r_timeunit.value,
            feed=r_feed.value,
            page=r_page,
            items=page_items,
            last_updated=last_hour,
            topnav_title=get_topnav_title(page_date, r_timeunit),
            dates=page_dates,
            langs_disp=displayed_languages(current_user.UserID),
            tags_disp=displayed_tags(current_user.UserID),
            feeds_all=all_feeds(),
            tags_all=all_tags(current_user.UserID)
    )

@app.route("/settings")
@auth_required()
def settings():
    r_feed = get_feed()
    r_langs = get_langs()
    r_page = get_page()
    r_tags = get_tags()
    r_timeunit = get_timeunit()

    return render_template("settings.html",
            timeunit=r_timeunit.value,
            feed=r_feed.value,
            page=r_page,
            topnav_title=current_user.Name,
            feeds_all=all_feeds(),
            tags_all=all_tags(current_user.UserID),
            langs_all=[e.value for e in Language],
            feeds_lang=all_feeds_lang(current_user.UserID)
    )

@app.route("/statistics")
@auth_required()
def statistics():
    r_feed = get_feed()
    r_langs = get_langs()
    r_page = get_page()
    r_tags = get_tags()
    r_timeunit = get_timeunit()

    return render_template("statistics.html",
            timeunit=r_timeunit.value,
            feed=r_feed.value,
            page=r_page,
            langs_all=[e.value for e in Language],
            likes_lang=all_likes_lang(current_user.UserID)
    )

#<?php
#$items = array();
#$unclassified = array();
#for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
#    $items[] = $row_it;
#    if ($feed != 'Full' and is_null($row_it['Score'])) {
#        $unclassified[] = $row_it['ItemID'];
#    }
#}
#
#// Classifiers.
#if (!empty($unclassified)) {
#    $db->exec("END");
#    $bash_cmd = "python3 " . $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/aux/apply_magic.py " . escapeshellarg($user_id) . " " . escapeshellarg($clf) . " " . escapeshellarg(json_encode($unclassified));
#    $res = shell_exec($bash_cmd);
#    $classified = json_decode($res, true);
#    $db->exec("BEGIN");
#
#    for ($i = 0; $i < count($unclassified); $i++) {
#        $j = array_search($unclassified[$i], array_column($items, 'ItemID'));
#        $items[$j]['Score'] = $classified[$i];
#    }
#
#    if ($feed == 'Magic') {
#        array_multisort(array_column($items, 'Score'), SORT_DESC, $items);
#    }
#}
#
#// Surprise.
#function choice($probs_partial, $val) {
#    $low = 0;
#    $high = count($probs_partial) - 1;
#
#    while (true) {
#        if ($high == $low + 1) {
#            break;
#        }
#
#        $temp = intdiv($low + $high, 2);
#        if ($probs_partial[$temp] <= $val) {
#            $low = $temp;
#        } else {
#            $high = $temp;
#        }
#    }
#
#    return $low;
#}
#
#if ($feed == 'Surprise') {
#    $probs_partial = array();
#    $probs_partial[] = 0.;
#    for ($item_ct = 0; $item_ct < count($items); $item_ct++) {
#        $item_it = $items[$item_ct];
#        $log_score = log($item_it['Score'] / (1. - $item_it['Score']));
#        $probs_partial[] = $probs_partial[$item_ct] + exp(-$log_score * $log_score);
#    }
#    $probs_total = $probs_partial[count($items)];
#
#    $items_temp = array();
#    $indices = array();
#    while (true) {
#        $val = rand() / getrandmax() * $probs_total;
#        $idx = choice($probs_partial, $val);
#
#        if (in_array($idx, $indices)) {
#            continue;
#        } else {
#            $items_temp[] = $items[$idx];
#            $indices[] = $idx;
#        }
#
#        if (count($indices) == 10) {
#            break;
#        }
#    }
#    $items = $items_temp;
#}
#
#function empty_leaves($node) {
#    for ($i = $node->childNodes->length - 1; $i >= 0; $i--) {
#        empty_leaves($node->childNodes[$i]);
#    }
#
#    if (!$node->hasChildNodes() and $node->textContent == "") {
#        $node->parentNode->removeChild($node);
#    }
#}
#?>







def get_topnav_title(page_date, timeunit):
    from datetime import datetime, timedelta

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
        if current_date >= page_date and current_date < page_date + timedelta(month=1):
            topnav_title = "This month"
        elif current_date - timedelta(months=1) >= page_date and current_date - timedelta(months=1) < page_date + timedelta(months=1):
            topnav_title = "Last month"
        else:
            topnav_title = page_date.strftime("%B %Y")
    else:
        raise ValueError

    return topnav_title
