from typing import Callable, cast, Union
from flask import Flask, Blueprint, request

from depytg.types import Update


def get_app(name: str, url_path: str, on_update: Callable[[Update], None]):
    app = Flask(name)

    get_blueprint(name, url_path, on_update, app)


def get_blueprint(name: str, url_path: str, on_update: Callable[[Update], None], bp: Union[Flask, Blueprint] = None):
    if not bp:
        bp = Blueprint(name, name)

    @bp.route("/{}".format(url_path), methods=['POST'])
    @bp.route("/{}/".format(url_path), methods=['POST'])
    def webhook():
        j = request.json()
        on_update(cast(Update, Update.from_json(j)))

    return bp
