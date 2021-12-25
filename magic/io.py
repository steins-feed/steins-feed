#!/usr/bin/env python3

import os
import pickle
import sklearn

from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

dir_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "clf.d",
)

def read_classifier(
    user: orm_users.User,
    lang: schema_feeds.Language,
) -> sklearn.pipeline.Pipeline:
    clf_path = os.path.join(
        dir_path,
        str(user.UserID),
        lang.name + ".pickle",
    )
    with open(clf_path, "rb") as f:
        return pickle.load(f)

def write_classifier(
    clf: sklearn.pipeline.Pipeline,
    user_id: orm_users.User,
    lang: schema_feeds.Language,
):
    clf_path = os.path.join(
        dir_path,
        str(user.UserID),
        lang.name + ".pickle",
    )
    with open(clf_path, "wb") as f:
        pickle.dump(clf, f)

