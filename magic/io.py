#!/usr/bin/env python3

"""Interaction with file system."""

import datetime
import os
import pickle
import sklearn

from model import recent
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

dir_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "clf.d",
)

def mkdir_p(dir_path: str):
    """
    Make directory if non-existent.

    Args:
      s: Absolute path of new directory.
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

def classifier_path(
    user: orm_users.User = None,
    lang: schema_feeds.Language = None,
) -> str:
    if user is None:
        user_id = "*"
    else:
        user_id = user.UserID

    if lang is None:
        lang_name = "*"
    else:
        lang_name = lang.name

    user_path = os.path.join(
        dir_path,
        str(user_id),
    )
    clf_path = os.path.join(
        user_path,
        lang_name + ".pickle",
    )

    mkdir_p(dir_path)
    if user:
        mkdir_p(user_path)

    return clf_path

def read_classifier(
    user: orm_users.User,
    lang: schema_feeds.Language,
) -> sklearn.pipeline.Pipeline:
    clf_path = classifier_path(user, lang)
    with open(clf_path, "rb") as f:
        return pickle.load(f)

def write_classifier(
    clf: sklearn.pipeline.Pipeline,
    user: orm_users.User,
    lang: schema_feeds.Language,
):
    clf_path = classifier_path(user, lang)
    with open(clf_path, "wb") as f:
        pickle.dump(clf, f)

def get_mtime(
    user: orm_users.User,
    lang: schema_feeds.Language,
) -> datetime.datetime:
    clf_path = classifier_path(user, lang)
    file_timestamp = os.stat(clf_path).st_mtime
    file_datetime = datetime.datetime.utcfromtimestamp(file_timestamp)

    return file_datetime

def is_up_to_date(
    user: orm_users.User,
    lang: schema_feeds.Language,
    dt: datetime.datetime = None,
) -> bool:
    try:
        file_datetime = get_mtime(user, lang)
    except FileNotFoundError:
        return False

    if dt is None:
        #dt = recent.last_liked(user, lang)
        dt = recent.last_liked(user.UserID)

    return file_datetime > dt

