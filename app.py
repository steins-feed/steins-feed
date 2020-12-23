#!/usr/bin/env python3

from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, auth_required
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from model import get_engine, get_table

#Create app.
app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw'
app.config['SECURITY_PASSWORD_SALT'] = '146585145368132386173505678016728509634'

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=get_engine()))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
    __table__ = get_table('Users')

class Role():
    pass

# Set up Flask-Security.
user_datastore = SQLAlchemyUserDatastore(get_engine(), User, Role)
security = Security(app, user_datastore)

@app.route("/")
@auth_required()
def home():
    return "Hello world."

if __name__ == "__main__":
    app.run()
