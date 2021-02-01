#!/usr/bin/env python3

from dotenv import load_dotenv
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_security import LoginForm, RegisterForm
from flask_security import UserMixin, RoleMixin
import os
from sqlalchemy.orm import relationship, synonym
from wtforms import StringField
from wtforms.validators import DataRequired

from model import get_model, get_session, get_table

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    ".env"
))

def get_user_datastore():
    global user_datastore
    if 'user_datastore' not in globals():
        User = get_model('Users', [UserMixin])
        Role = get_model('Roles', [RoleMixin])

        User.id = synonym('UserID')
        User.name = synonym('Name')
        User.password = synonym('Password')
        User.email = synonym('Email')
        User.active = synonym('Active')
        User.roles = relationship(
                'Roles',
                secondary=get_table('Users2Roles'),
                back_populates='users')

        Role.users = relationship(
                'Users',
                secondary=get_table('Users2Roles'),
                back_populates='roles')

        user_datastore = SQLAlchemySessionUserDatastore(get_session(), User, Role)
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
        app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'Name'

        user_datastore = get_user_datastore()
        security = Security(app, user_datastore,
                login_form=ExtendedLoginForm,
                register_form=ExtendedRegisterForm
        )
    return security
