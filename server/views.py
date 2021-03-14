from http import HTTPStatus

from flask import Response
from flask import jsonify

from server import api
from server import app
from server.database import sqlite_db


@app.before_first_request
def _init_database():
    sqlite_db.init(app.config.get('DATABASE'))


@app.errorhandler(Exception)
def _return_json_if_error_occurred(e):
    if app.debug:
        # log errors
        app.log_exception(e)

    # JSON responses
    return jsonify(status=False,
                   message=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/')
def _index():
    return jsonify(status=True, message='AVDC')


@app.route('/people/<name>')
def _people(name: str):
    images = api.GetPeopleByName(name)
    if not images:
        return jsonify(status=False,
                       message=f'people not found: {name}'), HTTPStatus.NOT_FOUND
    return jsonify(images)


@app.route('/metadata/<_id>')
def _metadata(_id: str):
    m = api.GetMetadataByID(_id)
    if not m:
        return jsonify(status=False,
                       message=f'metadata not found: {_id}'), HTTPStatus.NOT_FOUND
    return jsonify(**m.toDict())


@app.route('/image/<_id>')
def _image(_id: str):
    data = api.GetImageByID(_id)
    if not data:
        return jsonify(status=False,
                       message=f'image not found: {_id}'), HTTPStatus.NOT_FOUND
    return Response(data, mimetype='image/jpeg')
