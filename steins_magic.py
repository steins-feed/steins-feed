#!/usr/bin/env python3

import numpy as np
import time

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from steins_sql import get_cursor, last_updated

def handle_naive_bayes(qd):
    c = get_cursor()

    likes = c.execute("SELECT Title FROM Items WHERE Like=1").fetchall()
    dislikes = c.execute("SELECT Title FROM Items WHERE Like=-1").fetchall()

    titles = []
    titles += [row_it[0] for row_it in likes]
    titles += [row_it[0] for row_it in dislikes]

    targets = np.zeros(len(likes) + len(dislikes))
    targets[:len(likes)] = 1
    targets[len(likes):] = -1

    # Build pipeline.
    count_vect = ('vect', CountVectorizer())
    tfidf_transformer = ('tfidf', TfidfTransformer())
    clf = ('clf', MultinomialNB())
    text_clf = Pipeline([count_vect, tfidf_transformer, clf])

    # Train classifier.
    clf = text_clf.fit(titles, targets)

    # Test on training data.
    #predicted = text_clf.predict(titles)
    #print(predicted[:len(likes)])
    #print(predicted[len(likes):])
    #predicted_proba = text_clf.predict_proba(titles)
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[:len(likes)]])
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[len(likes):]])

    # Make predictions.
    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    page_no = int(qd['page'])
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (d_it, )).fetchall()
    new_titles = [row_it[1] for row_it in items]
    predicted_proba = text_clf.predict_proba(new_titles)
    proba = [it[1] - it[0] for it in predicted_proba]
    proba_map = zip(proba, range(len(proba)))
    proba_map_sorted = sorted(proba_map, reverse=True)

    # Page.
    s = ""
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">"
    s += "<title>Stein's Feed</title>\n"
    s += "</head>\n"
    s += "<body>\n"

    s += "<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d")))
    s += "<p>{} articles. {} pages. Last updated: {}.</p>\n".format(len(items), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated()))

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"
    s += "<hr>\n"

    for item_ctr in proba_map_sorted:
        item_it = items[item_ctr[1]]

        s += "<h2><a href=\"{}\">{}</a></h2>\n".format(item_it[5], item_it[1])
        s += "<p>Source: {}. Published: {}. Score: {:.2f}.</p>".format(item_it[4], item_it[2], item_ctr[0])
        s += "{}".format(item_it[3])

        s += "<p>\n"
        s += "<form target=\"foo\">\n"
        s += "<input type=\"hidden\" name=\"id\" value=\"{}\">\n".format(item_it[0])
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" value=\"Like\">\n"
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/dislike.php\" value=\"Dislike\">\n"
        s += "</form>\n"
        s += "</p>\n"
        s += "<hr>\n"

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"

    s += "<p>\n"
    s += "<a href=\"/steins-feed/settings.php\">Settings</a>\n"
    s += "<a href=\"/steins-feed/statistics.php\">Statistics</a>\n"
    s += "</p>\n"
    s += "<hr>\n"

    s += "<p>Bag of words:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/naive_bayes.php\" value=\"Naive Bayes\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<iframe name=\"foo\" style=\"display: none;\"></iframe>\n"
    s += "</body>\n"
    s += "</html>\n"

    return s

if __name__ == "__main__":
    handle_naive_bayes({'page': 1})
