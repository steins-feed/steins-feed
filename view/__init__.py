#!/usr/bin/env python3

from flask import Flask, render_template, request
from flask_security import auth_required, current_user
import os
import os.path as os_path

from model.utils import last_updated, updated_dates, updated_items
from .auth import get_security

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

@app.route("/")
@auth_required()
def home():
    page_no = int(request.args.get('page', 0))
    timeunit = request.args.get('timeunit', "Day")
    feed = request.args.get('feed', "Full")
    tags_disp = request.args.get('tags', [])

    last_hour = last_updated().replace(
            minute=0, second=0, microsecond=0
    )
    page_dates = updated_dates(current_user.UserID, timeunit, last_hour, page_no + 2)
    if len(page_dates) == page_no + 2:
        page_date = page_dates[-2]

    page_items = updated_items(current_user.UserID, timeunit, feed, tags_disp, page_date, last_hour)



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







    return render_template("index.html",
            feed="Full",
            items=page_items,
            last_updated=last_hour,
            page=page_no,
            topnav_title=get_topnav_title(page_date, timeunit)
    )

def get_topnav_title(page_date, timeunit):
    from datetime import datetime, timedelta

    current_date = datetime.now()
    if timeunit == "Day":
        if current_date >= page_date and current_date < page_date + timedelta(days=1):
            topnav_title = "Today"
        elif current_date >= page_date - timedelta(days=1) and current_date < page_date:
            topnav_title = "Yesterday"
        else:
            topnav_title = page_date.strftime("%a, %d %b %Y")
    elif timeunit == "Week":
        if current_date >= page_date and current_date < page_date + timedelta(days=7):
            topnav_title = "This week"
        elif current_date >= page_date - timedelta(days=7) and current_date < page_date:
            topnav_title = "Last week"
        else:
            topnav_title = page_date.strftime("Week %U, %Y")
    elif timeunit == "Month":
        if current_date >= page_date and current_date < page_date + timedelta(month=1):
            topnav_title = "This month"
        elif current_date >= page_date - timedelta(months=1) and current_date < page_date:
            topnav_title = "Last month"
        else:
            topnav_title = page_date.strftime("%B %Y")
    else:
        raise ValueError

    return topnav_title
