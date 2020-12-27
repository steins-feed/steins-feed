#!/usr/bin/env python3

from flask import Flask, redirect, url_for
import os

from .auth import get_security
from .base import bp as base_bp
from .home import bp as home_bp, clean_summary
from .overview import bp as over_bp

# Flask.
static_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "static"
))
templates_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "templates"
))
app = Flask(__name__,
        static_folder=static_path,
        template_folder=templates_path
)

# Flask Security.
security = get_security(app)

# Jinja2.
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.filters['clean'] = clean_summary
app.jinja_env.filters['contains'] = lambda a, b: set(a) >= set(b)
app.jinja_env.filters['day'] = lambda x: x.strftime("%a, %d %b %Y")

# Flask blueprints.
app.register_blueprint(base_bp)
app.register_blueprint(home_bp)
app.register_blueprint(over_bp)

@app.route("/")
def home():
    return redirect(url_for("home.home"))

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
#?>
