#!/usr/bin/env python3

import logging
import os

import sqlalchemy as sqla
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

# Metadata.
metadata = sqla.MetaData(bind=engine)
metadata.reflect()

# SQLite check foreign keys.
@sqla.event.listens_for(sqla.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session.
session_factory = sqla_orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Session = sqla_orm.scoped_session(session_factory)

# Declarative base.
Base = sqla_orm.declarative_base(metadata=metadata)
Base.query = Session.query_property()

def get_model(name, mixins=[]):
    try:
        Model = globals()[name]
    except KeyError:
        Model = type(
            name,
            tuple([Base] + mixins),
            {'__table__': get_table(name)},
        )
        globals()[name] = Model
    return Model

def get_table(name):
    return sqla.Table(
        name,
        metadata,
        autoload=True,
    )
