from http import HTTPStatus

from flask import Response
from flask import jsonify
from flask import request
from werkzeug.exceptions import HTTPException

from avdc.utility import image
from server import api
from server import app
from server.database import database_init


@app.before_first_request
def _init_database():
    database_init(app.config.get('DATABASE'))


@app.before_request
def _check_token():
    token = app.config.get('TOKEN')
    if not token:
        return  # no authorization required

    header = request.headers.get('Authorization', default='', type=str)
    authorization = header.split(' ', maxsplit=1)

    if len(authorization) != 2 \
            or authorization[0] != 'Bearer' \
            or authorization[1] != token:
        return jsonify(status=False,
                       message='unauthorized'), HTTPStatus.UNAUTHORIZED


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
    return jsonify(status=True, message='AVDC-API')


@app.route('/actress/<name>')
def _actress(name: str):
    update = api.str_to_bool(
        request.args.get('update'))

    actress = api.GetActressByName(name, update=update)
    if not actress:
        return jsonify(status=False,
                       message=f'actress not found: {name}'), HTTPStatus.NOT_FOUND
    return jsonify(dict(actress))


@app.route('/image/actress/<name>')
@app.route('/image/actress/<name>/<int:index>')
def _actress_image(name: str, index: int = 0):
    actress = api.GetActressByName(name)
    if not actress or not actress.images:
        return jsonify(status=False,
                       message=f'actress image not found: {name}'), HTTPStatus.NOT_FOUND

    try:
        url = actress.images[index]
    except IndexError:
        return jsonify(status=False,
                       message=f'index out of range: {index}: {name}'), HTTPStatus.NOT_FOUND

    data = image.imageToBytes(
        image.autoCropImage(
            image.bytesToImage(
                image.getRawImageByURL(url))))
    return Response(data, mimetype=f'image/jpeg')


@app.route('/metadata/<vid>')
@api.extract_vid
def _metadata(vid: str):
    update = api.str_to_bool(
        request.args.get('update'))
    pos = request.args.get('pos', type=float)

    m = api.GetMetadataByVID(vid, update=update)
    if not m:
        return jsonify(status=False,
                       message=f'metadata not found: {vid}'), HTTPStatus.NOT_FOUND

    if pos is not None:
        api.UpdateCoverPositionByVID(m, pos)

    return jsonify(dict(m))


@app.route('/image/backdrop/<vid>')
@api.extract_vid
def _backdrop_image(vid: str):
    cover = api.GetBackdropImageByVID(vid)
    if not cover:
        return jsonify(status=False,
                       message=f'backdrop image not found: {vid}'), HTTPStatus.NOT_FOUND
    return Response(cover.data, mimetype=f'image/{cover.fmt}')


@app.route('/image/primary/<vid>')
@api.extract_vid
def _primary_image(vid: str):
    # dynamic generate primary image
    data = api.GetPrimaryImageByVID(vid)
    if not data:
        return jsonify(status=False,
                       message=f'primary image not found: {vid}'), HTTPStatus.NOT_FOUND
    return Response(data, mimetype=f'image/jpeg')


@app.route('/image/thumb/<vid>')
@api.extract_vid
def _thumb_image(vid: str):
    # dynamic generate thumb image
    data = api.GetThumbImageByVID(vid)
    if not data:
        return jsonify(status=False,
                       message=f'thumb image not found: {vid}'), HTTPStatus.NOT_FOUND
    return Response(data, mimetype=f'image/jpeg')


@app.route('/imageinfo/backdrop/<vid>')
@api.extract_vid
def _backdrop_image_info(vid: str):
    size = api.GetBackdropImageSizeByVID(vid)
    if not size:
        return jsonify(status=False,
                       message=f'backdrop image not found: {vid}'), HTTPStatus.NOT_FOUND
    height, width = size
    return jsonify(height=height, width=width)  # only size info for now


@app.route('/imageinfo/actress/<name>')
@app.route('/imageinfo/actress/<name>/<int:index>')
def _actress_image_info(name: str, index: int = 0):
    actress = api.GetActressByName(name)
    if not actress or not actress.images:
        return jsonify(status=False,
                       message=f'actress image not found: {name}'), HTTPStatus.NOT_FOUND

    try:
        url = actress.images[index]
    except IndexError:
        return jsonify(status=False,
                       message=f'index out of range: {index}: {name}'), HTTPStatus.NOT_FOUND

    height, width = image.getRemoteImageSizeByURL(url)

    scale = 2 / 3
    _width = int(height * scale)

    if _width >= width:
        height = int(width / scale)
    else:
        width = _width

    return jsonify(height=height, width=width)  # only size info for now
