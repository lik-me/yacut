import re
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits

from flask import abort, flash, redirect, render_template

from . import app, db
from .error_handlers import ERRORS_DESCRIPTIONS
from .forms import URLMapForm
from .models import URLMap

SHORT_MAX_LEN = 7


def url_map_generate():
    short = ""
    symbols = ascii_lowercase + ascii_uppercase + digits
    for _ in range(1, SHORT_MAX_LEN):
        short = short + choice(symbols)
    while short_already_exists(short) is False:
        return url_map_generate()
    return short


def url_ckeck(url):
    return re.match(r'http[s]?://.+', url)


def short_check(short):
    return re.match(r'^[A-Za-z0-9]+$', short)


def short_check_len(short):
    return len(short) < 16


def original_already_saved(original):
    return not URLMap.query.filter_by(original=original).first()


def short_already_exists(short):
    return not URLMap.query.filter_by(short=short).first()


@app.route('/', methods=['GET', 'POST'])
def index_view(url_map_new=None):
    form = URLMapForm()
    if form.validate_on_submit():
        original = form.original_link.data
        short = form.custom_id.data
        flash_msg = None
        flash_msg_cat = None
        if url_ckeck(original) is None:
            flash_msg = ERRORS_DESCRIPTIONS['url_format_wrong']
            flash_msg_cat = "original"
        if original_already_saved(original) is False:
            flash_msg = ERRORS_DESCRIPTIONS['url_already_saved']
            flash_msg_cat = "original"
        if short != "" and short is not None and short_check(short) is None:
            flash_msg = ERRORS_DESCRIPTIONS['short_wrong']
            flash_msg_cat = "short"
        elif short != "" and short is not None and short_check_len(short) is False:
            flash_msg = ERRORS_DESCRIPTIONS['short_very_long']
            flash_msg_cat = "short"
        elif short != "" and short_already_exists(short) is False:
            flash_msg = ERRORS_DESCRIPTIONS['short_occupate_html'].format(short)
            flash_msg_cat = "short"
        if flash_msg is not None:
            flash(flash_msg, flash_msg_cat)
            return render_template('index.html', form=form)
        if short == "" or short is None:
            short = url_map_generate()
        url_map = URLMap(
            original=original,
            short=short
        )
        db.session.add(url_map)
        db.session.commit()
        url_map_new = url_map.short
    return render_template('index.html', form=form, url_map_new=url_map_new)


@app.route('/<string:short>')
def original_view(short):
    original = URLMap.query.filter_by(short=short).first()
    if original is not None:
        return redirect(original.original)
    abort(404)
