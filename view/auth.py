#!/usr/bin/env python3

import os

import bleach
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_security import LoginForm, RegisterForm
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, synonym
from wtforms import StringField
from wtforms.validators import DataRequired

from model import get_table
from model import Base, Session

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    ".env",
))

class User(Base, UserMixin):
    __table__ = get_table("Users")

    id = synonym('UserID')
    name = synonym('Name')
    password = synonym('Password')
    email = synonym('Email')
    active = synonym('Active')

    roles = relationship(
        "Roles",
        secondary=get_table("Users2Roles"),
        back_populates="users",
    )

class Role(Base, RoleMixin):
    __table__ = get_table("Roles")

    users = relationship(
        "Users",
        secondary=get_table("Users2Roles"),
        back_populates="roles",
    )

def get_user_datastore():
    global user_datastore
    if 'user_datastore' not in globals():
        user_datastore = SQLAlchemySessionUserDatastore(Session, User, Role)
    return user_datastore

class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [DataRequired()])

class ExtendedRegisterForm(RegisterForm):
    name = StringField('Username', [DataRequired()])

def get_security(app):
    global security
    if 'security' not in globals():
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

        app.config['SECURITY_REGISTERABLE'] = True
        app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
        app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = [{
            "Name": {"mapper": lambda x: bleach.clean(x, strip=True)}
        }]

        user_datastore = get_user_datastore()
        security = Security(app, user_datastore,
                login_form=ExtendedLoginForm,
                register_form=ExtendedRegisterForm
        )
    return security
