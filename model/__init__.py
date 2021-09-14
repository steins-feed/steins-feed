#!/usr/bin/env python3

import logging
import os

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

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

# Contextual/thread-local sessions.
session_factory = sqla_orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Session = sqla_orm.scoped_session(session_factory)

# Declarative base.
Base = sqla_orm.declarative_base(metadata=metadata)
Base.query = Session.query_property()

# Connection.
def get_connection():
    return engine.connect()

# Session.
def get_session():
    return sqla_orm.Session(engine)

# Table.
def get_table(name):
    return sqla.Table(
        name,
        metadata,
        autoload=True,
    )
