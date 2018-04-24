from typing import Callable, cast, Union
from flask import Flask, Blueprint, request

from depytg.types import Update


def get_app(name: str, token: str, on_update: Callable[[Update], None]):
    app = Flask(name)

    get_blueprint(name, token, on_update, app)


def get_blueprint(name: str, token: str, on_update: Callable[[Update], None], bp: Union[Flask, Blueprint] = None):
    if not bp:
        bp = Blueprint(name, name)

    @bp.route("/{}".format(token), methods=['POST'])
    @bp.route("/{}/".format(token), methods=['POST'])
    def webhook():
        j = request.json()
        on_update(cast(Update, Update.from_json(j)))

    return bp
