#!/usr/bin/env python3

import os
import os.path as os_path
import sqlalchemy as sqla

engine = None
metadata = None

db_path = "sqlite:///" + os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "steins.db"
))

def get_engine():
    global engine
    if not engine:
        engine = sqla.create_engine(db_path, echo=True)
    return engine

def get_metadata():
    global metadata
    if not metadata:
        metadata = sqla.MetaData()
    return metadata

def connect():
    return get_engine().connect()

def get_table(name):
    return sqla.Table(name, get_metadata(), autoload=True, autoload_with=get_engine())
