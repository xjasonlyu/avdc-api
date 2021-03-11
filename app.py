#!/usr/bin/env python3
from http import HTTPStatus

from flask import Flask
from flask import jsonify

from core import NotFound
from core import search

app = Flask(__name__)


@app.route('/<keyword>')
def index(keyword: str):
    try:
        metadata = search(keyword)
    except NotFound as e:
        return jsonify(status=False, message=str(e)), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify(status=False, message=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        return jsonify(**metadata), HTTPStatus.OK


if __name__ == '__main__':
    app.run()
