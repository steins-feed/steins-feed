#!/usr/bin/env python3

from flask import Flask
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_security import auth_required

from model import get_model, get_session

#Create app.
app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw'
app.config['SECURITY_PASSWORD_SALT'] = '146585145368132386173505678016728509634'

User = get_model('Users')
Role = type("", (object, ), {})

# Set up Flask-Security.
user_datastore = SQLAlchemySessionUserDatastore(get_session(), User, Role)
security = Security(app, user_datastore)

@app.route("/")
@auth_required()
def home():
    return "Hello world."

if __name__ == "__main__":
    app.run()
