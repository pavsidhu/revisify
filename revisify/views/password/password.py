# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, url_for
from flask.ext.login import login_required, current_user, logout_user
from flask.ext.bcrypt import Bcrypt
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
from revisify import app

ts = URLSafeTimedSerializer(str(app.config['SECRET_KEY']))
bcrypt = Bcrypt()

password = Blueprint('password', __name__)

@password.route('/forgot-password', methods=['GET', 'POST'])
def forgot():
	form = passwordForm()

	if form.validate_on_submit():
		# Error message when email is not activated
		email = form.email.data.lower()
		user = db.session.query(User).filter_by(email=email, activated=True).one()
		passwordReset(user.id)
		flash('We\'ve send you an email to reset your password. Please check your spam folder if you don\'t see it.')


	return render_template('password/forgot.html', form=form)


@password.route('/reset-password/<token>', methods=['POST', 'GET'])
def reset(token):
	try:
		email = ts.loads(token, salt="OpoO4Mlr0BO3VQPNroSNndOxafYmhcb04vehKQEf5zjpDD1qckB0P5eprJbc", max_age=86400)
	except:
		return render_template('password/bad.html')

	form = resetPasswordForm()
	if form.validate_on_submit():
		password = bcrypt.generate_password_hash(form.password.data)
		user = db.session.query(User).filter_by(email=email, activated=True).one()
		user.password = password
		db.session.commit()
		flash('Your password has successfully been updated.')

	return render_template('password/reset.html', form=form)
