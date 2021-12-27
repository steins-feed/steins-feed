#!/usr/bin/env python3

import bleach
import dotenv
import flask
import flask_security
import os
import sqlalchemy as sqla
import wtforms

import model
from model.orm import users as orm_users

env_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    ".env",
)
dotenv.load_dotenv(env_path)

class FSUser(orm_users.User, flask_security.UserMixin):
    id = sqla.orm.synonym("UserID")
    name = sqla.orm.synonym("Name")
    password = sqla.orm.synonym("Password")
    email = sqla.orm.synonym("Email")
    active = sqla.orm.synonym("Active")

class FSRole(orm_users.Role, flask_security.RoleMixin):
    ...

def get_user_datastore() -> flask_security.SQLAlchemySessionUserDatastore:
    global user_datastore
    if "user_datastore" not in globals():
        user_datastore = flask_security.SQLAlchemySessionUserDatastore(
            model.Session,
            FSUser,
            FSRole,
        )
    return user_datastore

class ExtendedLoginForm(flask_security.LoginForm):
    email = wtforms.StringField(
        "Username",
        [wtforms.validators.DataRequired()],
    )

class ExtendedRegisterForm(flask_security.RegisterForm):
    name = wtforms.StringField(
        "Username",
        [wtforms.validators.DataRequired()],
    )

def get_security(app: flask.Flask) -> flask_security.Security:
    global security
    if "security" not in globals():
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")

        app.config["SECURITY_REGISTERABLE"] = True
        app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
        app.config["SECURITY_USER_IDENTITY_ATTRIBUTES"] = [
            {"Name": {"mapper": lambda x: bleach.clean(x, strip=True)}}
        ]

        user_datastore = get_user_datastore()
        security = flask_security.Security(
            app,
            user_datastore,
            login_form=ExtendedLoginForm,
            register_form=ExtendedRegisterForm,
        )
    return security

