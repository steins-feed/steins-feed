#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from log import get_handler

engine = None
metadata = None
session = None

db_path = "sqlite:///" + os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "steins.db"
))

sqla_logger = logging.getLogger('sqlalchemy')
sqla_logger.setLevel(logging.WARNING)
sqla_logger.addHandler(get_handler())

def get_connection():
    return get_engine().connect()

def get_engine():
    global engine
    if not engine:
        engine = sqla.create_engine(db_path)
    return engine

def get_metadata():
    global metadata
    if not metadata:
        metadata = sqla.MetaData(bind=get_engine())
    metadata.reflect()
    return metadata

def get_session():
    global session
    if not session:
        session_factory = sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=get_engine())
        session = scoped_session(session_factory)
    return session

def get_model(name):
    return type(name, (Base, ), {'__table__': get_table(name)})

def get_table(name):
    return sqla.Table(
            name,
            get_metadata(),
            autoload=True
    )

Base = declarative_base(metadata=get_metadata())
Base.query = get_session().query_property()
