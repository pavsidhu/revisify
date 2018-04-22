# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask.ext.login import current_user
from flask import Flask, request, session, redirect, url_for, g

from revisify import app
from revisify.utils import *

@app.before_request
def before_request():
    if not current_user.is_anonymous():
        if not current_user.activated:
            session['notificationBar'] = {
                'message': 'We sent your email a confirmation link. If you didn\'t receive an email <a onclick="confirmEmail()" class="underline">send another</a>.',
                'permanent': True
            }
    else:
        session['notificationBar'] = None

    try:
        x = session['hideNotificationBar']
        session['notificationBar'] = None
    except:
        pass

@app.after_request
def after_request(response):
    if g.sijax.is_sijax_request:
        if not g.sijax._sijax._callbacks:
            g.sijax.register_callback('confirmEmail', confirmEmail)
            g.sijax.register_callback('hideNotificationBar', hideNotificationBar)
            return g.sijax.process_request()
        else:
            return response
    else:
        return response
