#!/usr/bin/env python3

from flask import Flask
from flask_security import auth_required, current_user
import os
import os.path as os_path

from .auth import get_security

templates_path = os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "templates"
))
app = Flask(__name__, template_folder=templates_path)
security = get_security(app)

@app.route("/")
@auth_required()
def home():
    return "Hello {}!".format(current_user.Name)
