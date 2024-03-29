#!/usr/bin/env python3

from lxml import etree, html
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import typing

import model
from model.orm import items as orm_items, users as orm_users
from model.schema import feeds as schema_feeds

from . import io

def to_string(s: str) -> str:
    try:
        tree = html.fromstring(s)
        res = html.tostring(tree, encoding='unicode', method='text')
    except etree.ParserError as e:
        res = ""

    return res

def build_feature(row: orm_items.Item) -> str:
    """
    Build feature from item.

    Args:
      row: Item object.

    Returns:
      Feature string.
    """
    return to_string(row.Title)

def kullback_leibler(q: typing.Dict[str, float], p: typing.Dict[str, float]) -> float:
    """
    Measures distance between two word distributions.

    Args:
      p: Original word distribution.
      q: Candidate word distribution.

    Returns:
        Kullback-Leibler divergence.
    """
    ev_q = np.sum(list(q.values()))
    ev_p = np.sum(list(p.values()))

    res = 0.
    for k in set(p) & set(q):
        pq = q[k] / ev_q
        pp = p[k] / ev_p
        res += pp * np.log(pp / pq)

    return res

def train_classifier(
    user_id: int,
    lang: schema_feeds.Language,
    likes: typing.List[orm_items.Item],
    dislikes: typing.List[orm_items.Item],
) -> Pipeline:
    """
    Trains classifier from likes and dislikes.

    Args:
      user_id: UserID.
      lang: Language.
      likes: List of liked items.
      dislikes: List of disliked items.

    Returns:
      Trained pipeline.
    """
    if not likes:
        raise ValueError("No likes.")

    if not dislikes:
        raise ValueError("No dislikes.")

    titles = []
    titles += [build_feature(row_it) for row_it in likes]
    titles += [build_feature(row_it) for row_it in dislikes]

    targets = []
    targets += [1 for row_it in likes]
    targets += [-1 for row_it in dislikes]

    # Build pipeline.
    count_vect = ('vect', CountVectorizer())
    #count_vect = ('vect', NLTK_CountVectorizer(lang_it))
    tfidf_transformer = ('tfidf', TfidfTransformer())
    nb_clf = ('clf', MultinomialNB(fit_prior=False))
    text_clf = Pipeline([count_vect, tfidf_transformer, nb_clf])

    # Train pipeline.
    text_clf.fit(titles, targets)
    return text_clf

def compute_score(
    user_id: int,
    lang: schema_feeds.Language,
    items: typing.List[orm_items.Item],
) -> typing.List[float]:
    """
    Computes item score using classifier.

    Args:
      user_id: User ID.
      lang: Language.
      items: List of item objects.

    Returns:
      List of scores between -1.0 and +1.0.
    """
    with model.get_session() as session:
        user = session.get(orm_users.User, user_id)
    clf = io.read_classifier(user, lang)

    titles = [build_feature(row_it) for row_it in items]
    targets = clf.predict_proba(titles)
    scores = 2. * targets[:, 1] - 1.

    return scores
