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

from model import Session
from model.orm import users

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    ".env",
))

class FSUser(users.User, UserMixin):
    id = synonym('UserID')
    name = synonym('Name')
    password = synonym('Password')
    email = synonym('Email')
    active = synonym('Active')

class FSRole(users.Role, RoleMixin):
    ...

def get_user_datastore():
    global user_datastore
    if 'user_datastore' not in globals():
        user_datastore = SQLAlchemySessionUserDatastore(Session, FSUser, FSRole)
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
