# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, request, flash, g
from flask.ext.login import login_user, logout_user, login_required
from sijax.plugin.upload import register_upload_callback
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
import flask_sijax, cStringIO

account = Blueprint('account', __name__)
#
# @account.route('/register', methods=['POST', 'GET'])
# def register():
# 	form = registerForm()
#
# 	if form.validate_on_submit():
# 		session.clear()
# 		name = form.name.data
# 		email = form.email.data
# 		password = form.password.data
# 		remember = form.remember.data
# 		createAccount(name=name,
# 					  email=email,
# 					  password=password,
# 					  remember=remember)
# 		return redirect(url_for('account.setupProfile'))
#
# 	return render_template('account/register.html', form=form)

@account.route('/setup-profile', methods=['POST', 'GET'])
@login_required
def setupProfile():
	profilePictureForm = setupProfilePictureForm()
	userDetailsForm = setupUserDetailsForm()

	def profilePicture(response, files, form):
		if profilePictureForm.validate_on_submit():
			picture = files['file']
			crop = profilePictureForm.crop.data
			newProfilePicture(picture, crop)

	if userDetailsForm.validate_on_submit():
		current_user.education = userDetailsForm.education.data.strip()
		current_user.location = userDetailsForm.location.data

		db.session.commit()

		return redirect('/')

	formInit = g.sijax.register_upload_callback('profilePicture', profilePicture)

	if g.sijax.is_sijax_request:
		return g.sijax.process_request()

	return render_template('account/setupProfile.html', profilePictureForm=profilePictureForm, userDetailsForm=userDetailsForm, formInit=formInit)


@account.route('/sign-in', methods=['POST', 'GET'])
def signIn():
	form = loginForm(csrf_enabled=False)
	if form.validate_on_submit():
		# Get data from from
		email = form.email.data
		password = form.password.data
		remember = form.remember.data

		# Get user with email
		users = User.query.filter_by(email=email).all()
		# If there is a user password is correct
		if users is not None:
			for user in users:
				if user.verifyPassword(password):
					# If email is banned
					if db.session.query(Ban).filter_by(userID=user.id).first():
						return render_template('account/banned.html')

					# Remove all session variables to prevent errors
					try:
						x = session['dev']
						session.clear()
						session['dev'] = True
					except:
						session.clear()

					signInUser(user, remember)

					# Redirects to last page or main page
					return redirect(request.args.get('next') or url_for('main.index'))
				else:
					form.password.errors.append('The password for this account is incorrect.')
		else:
			if user is None:
				form.email.errors.append('There is no account registered with this email.')
			else:
				form.password.errors.append('The password for this account is incorrect.')

	return render_template('account/signIn.html', form=form)


@account.route('/sign-out', methods=['POST', 'GET'])
def signOut():
	session.clear()
	logout_user()
	return render_template('account/signOut.html')


@account.route('/banned', methods=['POST', 'GET'])
@login_required
def banned():
	if current_user.banned:
		return render_template('account/banned.html')
	else:
		return redirect(url_for('main.index'))


# Change profile picture form for mobile devices. The default change profile
# picture popup for desktops does not work well on mobile.
@account.route('/change-profile-picture', methods=['POST', 'GET'])
@login_required
def changeProfilePicture():
	profilePictureForm = setupProfilePictureForm()

	if profilePictureForm.validate_on_submit():

		picture = request.files['file']
		crop = profilePictureForm.crop.data
		newProfilePicture(picture, crop)

		return redirect(url_for('social.user', hash=current_user.hash))

	return render_template('account/changeProfilePicture.html', profilePictureForm=profilePictureForm)


# Edit user details form for mobile devices.
@account.route('/edit-my-details', methods=['POST', 'GET'])
@login_required
def editUserDetails():
	userDetailsForm = profileUserDetailsForm()

	if userDetailsForm.validate_on_submit():
		name = userDetailsForm.name.data.strip()
		location = userDetailsForm.location.data.strip()
		education = userDetailsForm.education.data.strip()

		if name != '' and name != None:
			user.name = name

		if location != '' and location != None:
			user.location = location

		if education != '' and education != None:
			user.education = education

		current_user.name = name
		current_user.location = location
		current_user.education = education
		db.session.commit()

		return redirect(url_for('social.user', hash=current_user.hash))

	return render_template('account/editUserDetails.html', userDetailsForm=userDetailsForm)


# Edit weekly goal for mobile devices.
@account.route('/edit-my-weekly-goal', methods=['POST', 'GET'])
@login_required
def editWeeklGoal():
	def editWeeklyGoal(response, goal):
		current_user.weeklyGoal = goal
		db.session.commit()
		response.redirect('/')

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('editWeeklyGoal', editWeeklyGoal)
		return g.sijax.process_request()

	return render_template('account/editWeeklyGoal.html')


# About weekly goal for mobile devices.
@account.route('/about-my-weekly-goal', methods=['POST', 'GET'])
@login_required
def aboutWeeklGoal():
	return render_template('account/aboutWeeklyGoal.html')
