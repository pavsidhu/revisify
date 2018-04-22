# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import render_template
from revisify import app

@app.route('/403')
@app.errorhandler(403)
def forbidden(e):
    return render_template('error/403.html'), 403


@app.route('/404')
@app.errorhandler(404)
def notFound(e=''): # e is set to '' so if sent to page without error, you're not redirected to /500
    return render_template('error/404.html'), 404


@app.route('/500')
@app.errorhandler(500)
def internalServer(e):
    return render_template('error/500.html'), 500
