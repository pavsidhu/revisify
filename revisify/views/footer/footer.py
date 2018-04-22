# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session
from flask.ext.login import login_required
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
from flask import session, redirect
from functools import wraps
import requests, calendar

footer = Blueprint('footer', __name__)

@footer.route('/privacy-policy')
def privacyPolicy():
	return render_template('footer/privacyPolicy.html')


@footer.route('/terms-of-service')
def terms():
	return render_template('footer/terms.html')


@footer.route('/contact', methods=['POST', 'GET'])
def contact():
	form = contactForm()

	if form.validate_on_submit():
		contactEmail(form.name.data, form.email.data, form.message.data)
		return render_template('footer/emailSent.html')

	if not current_user.is_anonymous():
		name = current_user.name
		email = current_user.email
		return render_template('footer/contact.html', form=form, name=name, email=email)
	else:
		return render_template('footer/contact.html', form=form)
