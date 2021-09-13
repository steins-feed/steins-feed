#!/usr/bin/env python3

import logging
import os

import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import log

# Logger.
logger = log.Logger("sqlalchemy", logging.WARNING)

# Engine.
db_path = "sqlite:///" + os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "steins.db",
)
engine = sqla.create_engine(db_path, connect_args={
    "check_same_thread": False,
    "timeout": 5,
})

@sqla.event.listens_for(sqla.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_metadata():
    global metadata
    if 'metadata' not in globals():
        metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    return metadata

def get_model(name, mixins=[]):
    try:
        Model = globals()[name]
    except KeyError:
        Model = type(
            name,
            tuple([get_base()] + mixins),
            {'__table__': get_table(name)}
        )
        globals()[name] = Model
    return Model

def get_session():
    global session
    if 'session' not in globals():
        session_factory = sessionmaker(autocommit=False,
                autoflush=False,
                bind=engine
        )
        session = scoped_session(session_factory)
    return session

def get_table(name):
    return sqla.Table(
            name,
            get_metadata(),
            autoload=True
    )

def get_base():
    global Base
    if 'Base' not in globals():
        Base = declarative_base(metadata=get_metadata())
        Base.query = get_session().query_property()
    return Base
