#!/usr/bin/env python3

import html

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from steins_sql import get_cursor

def unescape(s):
    return html.unescape(html.unescape(s))

def build_feature(row):
    title = row['Title'] + " " + row['Summary']
    idx1 = title.find("<")
    while not idx1 == -1:
        idx2 = title.find(">", idx1)
        title = title[:idx1] + title[idx2+1:]
        idx1 = title.find("<")
    return unescape(title)

def handle_magic(qd):
    c = get_cursor()
    user = qd['user']

    clfs = dict()
    langs = [e[0] for e in c.execute("SELECT DISTINCT Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}!=0".format(user)).fetchall()]

    for lang_it in langs:
        # Build pipeline.
        count_vect = ('vect', CountVectorizer())
        tfidf_transformer = ('tfidf', TfidfTransformer())
        if qd['classifier'] == 'Naive Bayes':
            clf = ('clf', MultinomialNB())
        elif qd['classifier'] == 'Logistic Regression':
            clf = ('clf', LogisticRegression())
        else:
            raise KeyError
        text_clf = Pipeline([count_vect, tfidf_transformer, clf])

        # Train classifiers.
        likes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=1 AND Language=?".format(user), (lang_it, )).fetchall()
        dislikes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=-1 AND Language=?".format(user), (lang_it, )).fetchall()

        titles = []
        titles += [build_feature(row_it) for row_it in likes]
        titles += [build_feature(row_it) for row_it in dislikes]

        targets = []
        targets += [1 for row_it in likes]
        targets += [-1 for row_it in dislikes]

        try:
            clf = text_clf.fit(titles, targets)
        except ValueError:
            continue
        clfs[lang_it] = clf

    return clfs

    # Test on training data.
    #predicted = text_clf.predict(titles)
    #print(predicted[:len(likes)])
    #print(predicted[len(likes):])
    #predicted_proba = text_clf.predict_proba(titles)
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[:len(likes)]])
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[len(likes):]])

def steins_generate_page(page_no="0", lang="International", user="nobody", scorer=[]):
    c = get_cursor()
    page_no = int(page_no)

    # Preamble.
    s = "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">\n"
    s += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>\n"
    s += "<link rel=\"stylesheet\" type=\"text/css\" href=\"/steins-feed/index.css\"/>\n"
    s += "<title>Stein's Feed</title>\n"

    # Open menu.
    s += "<script>\n"
    s += "function open_menu() {\n"
    s += "    var stat = document.getElementById('sidenav');\n"
    s += "    stat.style.width = \"250px\";\n"
    s += "}\n"
    s += "</script>\n"

    # Close menu.
    s += "<script>\n"
    s += "function close_menu() {\n"
    s += "    var stat = document.getElementById('sidenav');\n"
    s += "    stat.style.width = \"0\";\n"
    s += "}\n"
    s += "</script>\n"

    s += "</head>\n"
    s += "<body>\n"

    #--------------------------------------------------------------------------

    # Top navigation menu.
    s += "<div class=\"topnav\"><h1>\n"
    s += "{}\n".format(user)
    s += "<span class=\"scroll\"></span>\n"
    s += "<span class=\"onclick\" onclick=\"open_menu()\">&#9776;</span>\n"
    s += "</h1></div>\n"

    #--------------------------------------------------------------------------

    # Side navigation menu.
    s += "<div id=\"sidenav\" class=\"sidenav\">\n"

    # Navigation.
    s += "<h1 class=\"sidenav\">\n"
    s += "<span class=\"onclick\" onclick=\"close_menu()\">&times;</span>\n"
    s += "</h1>\n"

    # Languages.
    s += "<p>\n"
    s += "Feeds:\n"
    s += "<ul>\n"
    s += "<li><a href=\"/steins-feed/index.php?user={}\">International</a></li>\n".format(user)
    langs = c.execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()
    for lang_it in langs:
        s += "<li><a href=\"/steins-feed/index.php?lang={0}&user={1}\">{0}</a></li>\n".format(lang_it[0], user)
    s += "</ul>\n"
    s += "</p>\n"

    # Naive Bayes.
    s += "<form>\n"
    s += "<p>Naive Bayes:</p>\n"
    s += "<p>\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"hidden\" name=\"classifier\" value=\"Naive Bayes\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Surprise\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/analysis.php\" name=\"submit\" value=\"Analysis\">\n"
    s += "</p>\n"
    s += "</form>\n"

    # Logistic Regression.
    s += "<form>\n"
    s += "<p>Logistic regression:\n</p>"
    s += "<p>\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"hidden\" name=\"classifier\" value=\"Logistic Regression\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Surprise\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/analysis.php\" name=\"submit\" value=\"Analysis\">\n"
    s += "</p>\n"
    s += "</form>\n"

    s += "<hr>\n"

    # Statistics & Settings.
    s += "<p><a href=\"/steins-feed/statistics.php?user={}\">Statistics</a></p>\n".format(user)
    s += "<p><a href=\"/steins-feed/settings.php?user={}\">Settings</a></p>\n".format(user)

    s += "</div>\n"

    #--------------------------------------------------------------------------

    # Body.
    s += "<div class=\"main\">\n"
    s += "<hr>\n"

    langs = scorer.keys()
    for lang_it in langs:
        s += "<h2>{}</h2>\n".format(lang_it)

        pipeline = scorer[lang_it]
        count_vect = pipeline.named_steps['vect']
        tfidf_transformer = pipeline.named_steps['tfidf']
        clf = pipeline.named_steps['clf']

        #table = count_vect.vocabulary_.items()
        #coeffs = clf.coef_[0] * tfidf_transformer.idf_
        #table = [(row[0], coeffs[row[1]], ) for row in table]
        #table = sorted(table, key=lambda row: row[2])
        table = list(count_vect.vocabulary_.keys())
        coeffs = pipeline.predict_log_proba(table)
        table = [(table[ct], coeffs[ct, 0], ) for ct in range(len(table))]
        table = sorted(table, key=lambda row: row[1])

        # Least favorite words.
        s += "<ol>\n"
        for row in table[:10]:
            s += "<li>{}</li>\n".format(row[0])
        s += "</ol>\n"

        # Most favorite words.
        s += "<ol>\n"
        for row in reversed(table[-10:]):
            s += "<li>{}</li>\n".format(row[0])
        s += "</ol>\n"

    s += "</div>\n"
    s += "</body>\n"
    s += "</html>\n"

    return s

def handle_analysis(qd):
    clfs = handle_magic(qd)
    print(steins_generate_page(user=qd['user'], scorer=clfs))

if __name__ == "__main__":
    clfs = handle_magic({'user': "hansolo", 'classifier': "Logistic Regression"})
    clf = clfs['English']
    count_vect = clf.named_steps['vect']
    tfidf_transformer = clf.named_steps['tfidf']
    lr_clf = clf.named_steps['clf']
    table = count_vect.vocabulary_.items()
    coeffs = lr_clf.coef_[0] * tfidf_transformer.idf_
    table = [row + (coeffs[row[1]], ) for row in table]
    table = sorted(table, key=lambda row: row[2])
    print("Least favorite:", [row[0] for row in table[:10]])
    print("Most favorite:", [row[0] for row in reversed(table[-10:])])
