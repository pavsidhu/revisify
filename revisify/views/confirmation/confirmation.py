# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, g
from flask.ext.login import login_required, current_user
from revisify.utils import *
from revisify.models import *
from revisify import app
import flask_sijax

ts = URLSafeTimedSerializer(str(app.config['SECRET_KEY']))

confirmation = Blueprint('confirmation', __name__)

@confirmation.route('/confirm/<token>', methods=['POST', 'GET'])
def confirm(token):
	try:
		token = ts.loads(token, salt='OpoO4Mlr0BO3VQPNroSNndOxafYmhcb04vehKQEf5zjpDD1qckB0P5eprJbc', max_age=86400)

		# 'Reactivate' is put infront of token string so that we know if to
		# Send a welcome email or not
		if str(token)[0:10] == 'reactivate':
			reactivate = True
			data = token[10:].split('+', 1)
			id = data[0]
			email = data[1]
		else:
			reactivate = False
			id = token


		user = db.session.query(User).filter_by(id=id).one()

		if reactivate:
			user.email = email

		user.activated = True
		db.session.commit()

		if not reactivate:
			welcomeEmail(user.id)

		session['notificationBar'] = {
			'message': 'Your email has successfully been confirmed!',
			'permanent': False
			}

		return redirect(url_for('main.index'))

	except:
		session['notificationBar'] = {
			'message': 'There\'s been an error! The confirmation link has expired or is incorrect. Try <a onclick="confirmEmail()" class="underline">send another email</a>.',
			'permanent': False
			}
		return redirect(url_for('main.index'))
