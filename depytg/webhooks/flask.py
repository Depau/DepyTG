from typing import Callable, cast
from flask import Flask, request

from depytg.types import Update


def get_app(name: str, token: str, on_update: Callable[[Update], None]):
    app = Flask(name)

    @app.route("/telegram/{}".format(token), methods=['POST'])
    @app.route("/telegram/{}/".format(token), methods=['POST'])
    def webhook():
        j = request.json()
        on_update(cast(Update, Update.from_json(j)))

    return app