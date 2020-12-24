#!/usr/bin/env python3

from flask_security import Security, SQLAlchemySessionUserDatastore, LoginForm
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, synonym
from wtforms import StringField
from wtforms.validators import DataRequired

from model import get_model, get_session, get_table

user_datastore = None
security = None

def get_user_datastore():
    global user_datastore
    if not user_datastore:
        User = get_model('Users', [UserMixin])
        Role = get_model('Roles', [RoleMixin])

        User.roles = relationship(
                'Roles',
                secondary=get_table('Users2Roles'),
                back_populates='users')
        User.id = synonym('UserID')
        User.password = synonym('Password')
        User.active = synonym('Active')

        Role.users = relationship(
                'Users',
                secondary=get_table('Users2Roles'),
                back_populates='roles')

        user_datastore = SQLAlchemySessionUserDatastore(get_session(), User, Role)
    return user_datastore

class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [DataRequired()])

def get_security(app):
    global security
    if not security:
        app.config['SECRET_KEY'] = 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw'
        app.config['SECURITY_PASSWORD_SALT'] = '146585145368132386173505678016728509634'
        app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'Name'

        user_datastore = get_user_datastore()
        security = Security(app, user_datastore, login_form=ExtendedLoginForm)
    return security
