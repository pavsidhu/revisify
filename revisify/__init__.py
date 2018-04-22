# Copyright (c) 2016 by Revisify. All Rights Reserved.

import config
import flask_sijax
import logging
import os

from flask import Flask, request
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import current_user, LoginManager
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from logging.handlers import SMTPHandler
from mimicdb import MimicDB

from revisify.jinja import configureJinja

version = '2.1-10'

db = SQLAlchemy(session_options={'autoflush': False})
bcrypt = Bcrypt()
oauth = OAuth()

loginManager = LoginManager()
loginManager.session_protect = 'strong'
loginManager.login_view = 'account.signIn'

def createApp(configuration=None):
    global app
    app = Flask(__name__)

    configureApp(app, configuration)
    configureJinja(app, version)
    configureLogging(app)

    db.init_app(app)
    bcrypt.init_app(app)
    loginManager.init_app(app)
    oauth.init_app(app)
    loginManager.init_app(app)
    MimicDB()

    # This allows Sijax to keep the JS files up to date
    app.config['SIJAX_STATIC_PATH'] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
    flask_sijax.Sijax(app)

    if app.config['MIGRATE_PRODUCTION']:
        migrate = Migrate(app, db, directory='/home/ubuntu/revisify/migrations')
    else:
        migrate = Migrate(app, db)

    import hooks
    import views
    import views.errors

    views = (
        views.account,
        views.admin,
        views.confirmation,
        views.footer,
        views.help,
        views.static,
        views.main,
        views.signInOauth,
        views.password,
        views.settings,
        views.social,
        views.subject,
        views.study,
        views.topic
    )

    for view in views:
        app.register_blueprint(view)

    return app


def configureApp(app, c):
    if c:
        c = c.lower()

    if c == 'development':
        app.config.from_object(config.Development)
    elif c == 'screenshot':
        app.config.from_object(config.Screenshot)
    elif c == 'testing':
        app.config.from_object(config.Testing)
    elif c == 'production' or c == None:
        app.config.from_object(config.Production)
    else:
        print 'Configuration options are: development, screenshot, testing, production.'


def configureLogging(app):
    class EmailHandler(SMTPHandler):
        def emit(self, record):
            if current_user.is_anonymous():
                userID = 'Anonymous'
            else:
                userID = current_user.id

            record.msg += """
                        IP: {ip}
                        User ID: {userID}
                        Agent: {agent}
                    """.format(
                        method = request.method,
                        path = request.path,
                        ip = request.remote_addr,
                        agentPlatform = request.user_agent.platform,
                        agentBrowser = request.user_agent.browser,
                        agentBrowserVersion = request.user_agent.version,
                        agent = request.user_agent.string,
                        userID=userID
                        )
            super(EmailHandler, self).emit(record)

    credentials = ('errors@revisify.com', '4hE76!B0G1P>@$`')
    mailHandler = EmailHandler(
        mailhost=('smtp.mailgun.org', 587),
        fromaddr='Revisify Errors <errors@revisify.com>',
        toaddrs=['pavsidhu@revisify.com'],
        subject='Application Error',
        credentials=credentials,
        secure=None)
    mailHandler.setLevel(logging.ERROR)
    app.logger.addHandler(mailHandler)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
