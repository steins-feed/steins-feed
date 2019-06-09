#!/usr/bin/env python3

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from steins_feed import steins_generate_page
from steins_sql import get_cursor

def build_feature(row):
    title = row['Title'] + " " + row['Summary']
    idx1 = title.find("<")
    while not idx1 == -1:
        idx2 = title.find(">", idx1)
        title = title[:idx1] + title[idx2+1:]
        idx1 = title.find("<")
    return title

def handle_magic(qd, classifier='Naive Bayes', surprise=-1):
    c = get_cursor()

    likes = c.execute("SELECT * FROM Items WHERE Like=1").fetchall()
    dislikes = c.execute("SELECT * FROM Items WHERE Like=-1").fetchall()

    titles = []
    titles += [build_feature(row_it) for row_it in likes]
    titles += [build_feature(row_it) for row_it in dislikes]

    targets = []
    targets += [1 for row_it in likes]
    targets += [-1 for row_it in dislikes]

    # Build pipeline.
    count_vect = ('vect', CountVectorizer())
    tfidf_transformer = ('tfidf', TfidfTransformer())
    if classifier == 'Naive Bayes':
        clf = ('clf', MultinomialNB())
    elif classifier == 'Logistic Regression':
        clf = ('clf', LogisticRegression())
    else:
        raise KeyError
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
    lang = qd['lang']
    if lang == "International":
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    else:
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1 AND Language=?) ORDER BY Published DESC", (lang, )).fetchall()
    page_no = int(qd['page'])
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    if lang == "International":
        items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (d_it, )).fetchall()
    else:
        items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1 AND Language=?) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (lang, d_it)).fetchall()
    new_titles = [build_feature(row_it) for row_it in items]
    predicted_proba = text_clf.predict_proba(new_titles)
    scores = [it[1] - it[0] for it in predicted_proba]
    score_sheet = zip(scores, range(len(scores)))
    score_board = sorted(score_sheet, reverse=True)

    # Page.
    return steins_generate_page(page_no, lang, score_board, surprise)

def handle_surprise(qd, classifier='Naive Bayes'):
    return handle_magic(qd, classifier, 10)

if __name__ == "__main__":
    handle_magic({'page': 1})
