import collections
from http import HTTPStatus

from flask import jsonify, request

from . import app, db
from .error_handlers import ERRORS_DESCRIPTIONS, InvalidAPIUsage
from .models import URLMap
from .views import (short_already_exists, short_check, short_check_len,
                    url_ckeck, url_map_generate)


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original(short_id):
    print(f"short_id = {short_id}")
    original = URLMap.query.filter_by(short=short_id).first()
    if original is not None:
        return jsonify({'url': original.original}), HTTPStatus.OK
    raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)


@app.route('/api/id/', methods=['POST'])
def add_url_map():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['api_data_absent'])
    if 'url' not in data:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['api_url_check'])
    original = data['url']
    if 'custom_id' not in data or data['custom_id'] == "" or data['custom_id'] is None:
        short = url_map_generate()
    else:
        short = data['custom_id']
    if url_ckeck(original) is None:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['url_format_wrong'])
    if short is not None and short_already_exists(short) is False:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['short_occupate_api'].format(short))
    if short is not None and short_check(short) is None:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['short_wrong'])
    if short is not None and short_check_len(short) is False:
        raise InvalidAPIUsage(ERRORS_DESCRIPTIONS['short_very_long'])
    data['short'] = short
    data['original'] = original
    url_map = URLMap()
    url_map.from_dict(data)
    db.session.add(url_map)
    db.session.commit()
    url_map_return = collections.defaultdict()
    url_map_dict = url_map.to_dict()
    new_record = URLMap.query.filter_by(original=original).first()
    new_record_short = new_record.short
    url_map_return['short_link'] = "http://" + str(request.host) + "/" + str(new_record_short)
    url_map_return['url'] = url_map_dict['original']
    return jsonify(url_map_return), HTTPStatus.CREATED
