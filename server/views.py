from http import HTTPStatus

from flask import Response
from flask import jsonify
from werkzeug.exceptions import HTTPException

from avdc.utility.misc import extractYear
from server import api
from server import app
from server.database import sqlite_db_init


@app.before_first_request
def _init_database():
    sqlite_db_init(app.config.get('DATABASE'))


@app.errorhandler(Exception)
def _return_json_if_error_occurred(e):
    if isinstance(e, HTTPException):
        status_code = e.code
    else:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        # log exception detail
        app.log_exception(e)

    # JSON response
    return jsonify(status=False,
                   message=str(e)), status_code


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
@api.extract_id
def _metadata(_id: str, c: bool):
    m = api.GetMetadataByID(_id)
    if not m:
        return jsonify(status=False,
                       message=f'metadata not found: {_id}'), HTTPStatus.NOT_FOUND

    if c:  # add chinese subtitle tag
        m.tags.append('中文字幕')

    return jsonify(**m.toDict(),
                   year=extractYear(m.release))


@app.route('/image/backdrop/<_id>')
@api.extract_id
def _backdrop(_id: str, _: bool):
    result = api.GetBackdropImageByID(_id)
    if not result:
        return jsonify(status=False,
                       message=f'backdrop image not found: {_id}'), HTTPStatus.NOT_FOUND
    fmt, data = result
    return Response(data, mimetype=f'image/{fmt}')


@app.route('/image/primary/<_id>')
@api.extract_id
def _primary(_id: str, _: bool):
    # dynamic generate primary image
    data = api.GetPrimaryImageByID(_id)
    if not data:
        return jsonify(status=False,
                       message=f'primary image not found: {_id}'), HTTPStatus.NOT_FOUND
    return Response(data, mimetype=f'image/jpeg')
