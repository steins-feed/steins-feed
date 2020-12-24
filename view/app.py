#!/usr/bin/env python3

from flask import Flask
from flask_security import Security, SQLAlchemySessionUserDatastore, LoginForm
from flask_security import auth_required, current_user
from flask_security import UserMixin, RoleMixin
import os
import os.path as os_path
from sqlalchemy.orm import relationship, synonym
from wtforms import StringField
from wtforms.validators import DataRequired

from model import get_model, get_session, get_table

#Create app.
templates_path = os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "templates"
))
app = Flask(__name__, template_folder=templates_path)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw'
app.config['SECURITY_PASSWORD_SALT'] = '146585145368132386173505678016728509634'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'Name'

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

class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [DataRequired()])

# Set up Flask-Security.
user_datastore = SQLAlchemySessionUserDatastore(get_session(), User, Role)
security = Security(app, user_datastore, login_form=ExtendedLoginForm)

@app.route("/")
@auth_required()
def home():
    return "Hello {}!".format(current_user.Name)

if __name__ == "__main__":
    app.run()
