# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session
from flask.ext.login import login_required, current_user
from flask.ext.bcrypt import Bcrypt
from sqlalchemy import or_
from revisify.utils import *
from revisify.models import *
from revisify.forms import *

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['POST', 'GET'])
@login_required
def accountSettings():

	passwordSuccess = False

	# If password changed or email updated, check which form submitted it.
	try:
		form = request.form['submit']
	except:
		form = None

	# If a form is submitted, set the point on the page to scroll to or manage
	# social connect buttons
	if form == 'changePassword':
		scroll = '#changePassword'

	elif form == 'changeEmail':
		scroll = '#changeEmail'

	elif form == 'addPassword':
		scroll = '#addPassword'

	elif form == 'socialConnectGoogle':
		session['settingsSocialConnect'] = True
		return redirect(url_for('signInOauth.authorize', provider='google'))

	elif form == 'socialConnectFacebook':
		session['settingsSocialConnect'] = True
		return redirect(url_for('signInOauth.authorize', provider='facebook'))

	else:
		scroll = ''

	emailForm = updateEmailForm()
	passwordForm = changePasswordForm()
	addPasswordForm = resetPasswordForm()

	if current_user.password:
		if passwordForm.validate_on_submit():
			newPassword = passwordForm.newPassword.data

			current_user.setPassword(newPassword)
			db.session.commit()

			flash('Your password has been changed successfully.', 'passwordForm')
	else:
		if addPasswordForm.validate_on_submit():
			newPassword = addPasswordForm.password.data

			current_user.setPassword(newPassword)
			db.session.commit()
			flash('Your password has been added.', 'addPasswordForm')

	if emailForm.validate_on_submit():
		newEmail = emailForm.email.data.lower()
		reactivateEmail(current_user.id, newEmail)
		flash('We\'ve send you an email! Please check your spam folder if you don\'t see it.', 'changeEmailForm')

	# Check if user has connected to Google
	googleAccount = socialConnected('google')

	# Check if user has connected to Facebook
	facebookAccount = socialConnected('facebook')

	return render_template('settings/settings.html',
							form=form,
							passwordForm=passwordForm,
							addPasswordForm=addPasswordForm,
							emailForm=emailForm,
							scroll=scroll,
							passwordSuccess=passwordSuccess,
							googleAccount=googleAccount,
							facebookAccount=facebookAccount)


@settings.route('/change-profile')
@login_required
def changeProfile():
	# Update database
	if current_user.profile:
		current_user.profile = False
		# Removes followers of that user
		db.session.query(Follow).filter_by(following=current_user.id).delete()
	else:
		current_user.profile = True

	db.session.commit()
	return redirect(url_for('settings.accountSettings'))


@settings.route('/delete-account', methods=['POST', 'GET'])
@login_required
def delete():
	form = deleteAccountForm()

	if form.validate_on_submit():
		db.session.query(User).filter_by(id=current_user.id).delete()
		db.session.commit()
		return redirect(url_for('account.signOut'))

	return render_template('settings/delete.html', form=form)
