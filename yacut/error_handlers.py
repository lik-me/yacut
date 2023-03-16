from http import HTTPStatus

from flask import jsonify, render_template

from . import app, db

ERRORS_DESCRIPTIONS = {
    'url_format_wrong': 'Ведена ссылка, не отвечающая правильному формату. Повторите, пожалуйста, ввод.',
    'url_already_saved': 'Такая ссылка уже есть в базе!',
    'short_wrong': 'Указано недопустимое имя для короткой ссылки',
    'short_very_long': 'Указано недопустимое имя для короткой ссылки',
    'short_occupate_api': 'Имя "{}" уже занято.',
    'short_occupate_html': 'Имя {} уже занято!',
    'api_data_absent': 'Отсутствует тело запроса',
    'api_url_check': '"url" является обязательным полем!'
}


class InvalidAPIUsage(Exception):
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
