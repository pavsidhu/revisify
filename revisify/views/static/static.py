# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, send_from_directory, url_for, request
from revisify import app

static = Blueprint('static', __name__)

@static.route('/robots.txt')
@static.route('/sitemap.xml')
@static.route('/logo.png')
def staticFiles():
    if request.path[1:] == 'logo.png':
        return send_from_directory(app.static_folder, 'images/logo.png')
    return send_from_directory(app.static_folder, request.path[1:])
