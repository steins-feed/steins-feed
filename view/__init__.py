#!/usr/bin/env python3

import flask
import os

from . import auth
from . import feed
from . import home
from . import overview
from . import tag

# Flask.
static_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "static",
)
templates_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "templates",
)
app = flask.Flask(
    __name__,
    static_folder=static_path,
    template_folder=templates_path,
)

# Flask Security.
security = auth.get_security(app)

# Jinja2.
app.jinja_env.line_statement_prefix = "#"
app.jinja_env.filters["contains"] = lambda a, b: set(a) >= set(b)
app.jinja_env.filters["day"] = lambda x: x.strftime("%a, %d %b %Y")

# Flask blueprints.
app.register_blueprint(feed.bp)
app.register_blueprint(home.bp)
app.register_blueprint(overview.bp)
app.register_blueprint(tag.bp)

@app.route("/")
def home() -> flask.Response:
    return flask.redirect(flask.url_for("home.home"))

