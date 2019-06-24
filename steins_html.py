#!/usr/bin/env python3

from lxml.html import builder as E

from steins_sql import get_cursor

lang_list = [
    "Afrikanns",
    "Albanian",
    "Arabic",
    "Armenian",
    "Basque",
    "Bengali",
    "Bulgarian",
    "Catalan",
    "Cambodian",
    "Chinese (Mandarin)",
    "Croation",
    "Czech",
    "Danish",
    "Dutch",
    "English",
    "Estonian",
    "Fiji",
    "Finnish",
    "French",
    "Georgian",
    "German",
    "Greek",
    "Gujarati",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Indonesian",
    "Irish",
    "Italian",
    "Japanese",
    "Javanese",
    "Korean",
    "Latin",
    "Latvian",
    "Lithuanian",
    "Macedonian",
    "Malay",
    "Malayalam",
    "Maltese",
    "Maori",
    "Marathi",
    "Mongolian",
    "Nepali",
    "Norwegian",
    "Persian",
    "Polish",
    "Portuguese",
    "Punjabi",
    "Quechua",
    "Romanian",
    "Russian",
    "Samoan",
    "Serbian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swahili",
    "Swedish ",
    "Tamil",
    "Tatar",
    "Telugu",
    "Thai",
    "Tibetan",
    "Tonga",
    "Turkish",
    "Ukranian",
    "Urdu",
    "Uzbek",
    "Vietnamese",
    "Welsh",
    "Xhosa"
]

def select_lang(feed_id=None, selected='English'):
    tree = E.SELECT(name="lang")
    if not feed_id is None:
        tree.name = "lang_{}".format(feed_id)

    for lang_it in lang_list:
        option_it = E.OPTION(value=lang_it)
        option_it.text = lang_it
        if lang_it == selected:
            option_it.set('selected')
        tree.append(option_it)

    return tree

def side_nav(user="nobody", lang="International", page_no=0, feed="Full", clf="Naive Bayes"):
    s = "<form>\n"
    c = get_cursor()

    # Language.
    s += "<p>Language:</p>\n"
    langs = ["International"]
    langs += [e[0] for e in c.execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()]
    for lang_it in langs:
        t = "<input type=\"radio\" name=\"lang\" value=\"{0}\">{0}<br>\n".format(lang_it)
        if lang_it == lang:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Feed.
    s += "<p>Feed:</p>\n"
    for feed_it in ["Full", "Magic", "Surprise"]:
        t = "<input type=\"radio\" name=\"feed\" value=\"{0}\">{0}<br>\n".format(feed_it)
        if feed_it == feed:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Algorithm.
    s += "<p>Algorithm:</p>\n"
    for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
        t = "<input type=\"radio\" name=\"clf\" value=\"{0}\">{0}<br>\n".format(clf_it)
        if clf_it == clf:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Button.
    s += "<p>\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Display\">\n"
    s += "</p>\n"

    s += "</form>\n"

    s += "<hr>\n"

    # Report.
    s += "<form><p>\n"
    s += "<select name=\"clf\">\n"
    for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
        t = "<option value=\"{0}\">{0}</option>\n".format(clf_it)
        if clf_it == clf:
            idx = t.find(">")
            t = t[:idx] + " selected" + t[idx:]
        s += t
    s += "</select>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/analysis.php\" value=\"Report\">\n"
    s += "</p></form>\n"

    s += "<hr>\n"

    # Statistics & Settings.
    s += "<p><a href=\"/steins-feed/statistics.php?user={}\">Statistics</a></p>\n".format(user)
    s += "<p><a href=\"/steins-feed/settings.php?user={}\">Settings</a></p>\n".format(user)

    return s
