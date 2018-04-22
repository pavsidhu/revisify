# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, send_from_directory, flash, g
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
import os, cStringIO, flask_sijax
from revisify import app
from PIL import Image

social = Blueprint('social', __name__)

@social.route('/user/<hash>', methods=['POST', 'GET'])
def user(hash):
	# Support for old URL structure
	# Checks if hash is the user ID
	try:
		user = userFromHash(hash)
		userID = user.id
	except:
		user = db.session.query(User).filter_by(id=hash).one()
		return redirect(url_for('social.user', hash=user.hash))

	def follow(response, id):
		if current_user.is_anonymous():
			return response.redirect(url_for('account.signIn'))

		if checkFollow(current_user.id, id):
			deleteFollow = Follow(current_user.id, id)
			Follow.query.filter_by(follower=current_user.id, following=id).delete()
			db.session.commit()
			response.attr('.followButton', 'style', '')
			response.html('.followButton', 'Follow')
		else:
			newFollow = Follow(current_user.id, id)
			db.session.add(newFollow)
			db.session.commit()
			response.attr('.followButton', 'style', 'background-color: #7CB342; color: white; border: 2px solid #558B2F;')
			response.html('.followButton', 'Following')

	report = reportForm()

	def reportUser(response, issue):
		if issue.strip() == '':
			response.html('#reportUserPopup .errorText', 'Please enter an issue.')
			response.css('#reportUserPopup .errorText', 'display', 'block')
			response.css('#reportUserPopup .successText', 'display', 'none')
		else:
			addReport(user.id, issue)
			db.session.commit()
			response.html('#reportUserPopup .successText', 'Thanks your issue has been received.')
			response.css('#reportUserPopup .successText', 'display', 'block')
			response.css('#reportUserPopup .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')


	def warnUser(response, reason):
		if current_user.admin:
			if reason.strip() == '':
				response.html('#warnUserPopup .errorText', 'Please enter a reason.')
				response.css('#warnUserPopup .errorText', 'display', 'block')
				response.css('#warnUserPopup .successText', 'display', 'none')
			else:
				addWarning(user.id, reason)
				db.session.commit()
				response.html('#warnUserPopup .successText', 'The user has been warned.')
				response.css('#warnUserPopup .successText', 'display', 'block')
				response.css('#warnUserPopup .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')


	def banUser(response, reason):
		if current_user.admin:
			if reason.strip() == '':
				response.html('#banUserPopup .errorText', 'Please enter a reason.')
				response.css('#banUserPopup .errorText', 'display', 'block')
				response.css('#banUserPopup .successText', 'display', 'none')
			else:
				addBan(user.id, reason)
				db.session.commit()
				response.html('#banUserPopup .successText', 'The user has been warned.')
				response.css('#banUserPopup .successText', 'display', 'block')
				response.css('#banUserPopup .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')


	if g.sijax.is_sijax_request:
		g.sijax.register_callback('follow', follow)

		g.sijax.register_callback('reportUser', reportUser)
		g.sijax.register_callback('warnUser', warnUser)
		g.sijax.register_callback('banUser', banUser)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)
		return g.sijax.process_request()

	profilePictureForm = setupProfilePictureForm()
	userDetailsForm = profileUserDetailsForm()

	if profilePictureForm.validate_on_submit():
		picture = request.files['picture']
		crop = profilePictureForm.crop.data
		newProfilePicture(picture, crop)

	if userDetailsForm.validate_on_submit():

		name = userDetailsForm.name.data.strip()

		# This prevents people leaving blank names
		if name != '':
			user.name = name

		user.education = userDetailsForm.education.data.strip()
		user.location = userDetailsForm.location.data

		db.session.commit()

	if current_user.is_anonymous(): # If not signed in
		ownAccount = False
	elif current_user.id == user.id: # If own account
		ownAccount = True
	else: # If signed in and not own account
		ownAccount = False

	# If user is private return a 404 not found page.
	if not ownAccount and user.profile == False:
		return abort(404)

	locationISO = user.location
	user.location = getLocation(user.location) # Get location from iso

	if not ownAccount:
		if current_user.is_anonymous():
			following = False
		elif db.session.query(Follow).filter_by(follower=current_user.id, following=user.id).first():
			following = True
		else:
			following = False

	# Receive following users
	followingUsers = followedUsers(userID)
	followingCount = len(followingUsers)

	# Receive followers
	followerUsers = userFollowers(userID)
	followerCount = len(followerUsers)

	# Get users subjects
	subjects = []
	for subject in getSubjectByAccount(userID):
		color = getColorByNumber(subject.color)
		percentage = getSubjectPercentage(subject.id)

		contentLink = url_for('subject.subjectList',
							  hash = subject.hash,
							  slug = subject.slug
							  )

		subjects.append({
			'id': subject.id,
			'name': subject.name,
			'hash': subject.hash,
			'slug': subject.slug,
			'contentLink': contentLink,
			'percentage': percentage,
			'textcolor': color['text'],
			'iconcolor': color['icon'],
		})

	if ownAccount:
		return render_template('social/user.html',
								user = user,
								subjects = subjects,
								followingUsers = followingUsers,
								followingCount = followingCount,
								followerUsers = followerUsers,
								followerCount = followerCount,
								locationISO = locationISO,
								ownAccount = ownAccount,
								profilePictureForm = profilePictureForm,
								userDetailsForm = userDetailsForm)
	elif current_user.is_anonymous() or not current_user.admin: # This check is put first to prevent error with anonymous user not having admin.
		return render_template('social/user.html',
								user = user,
								subjects = subjects,
								followingUsers = followingUsers,
								followingCount = followingCount,
								locationISO = locationISO,
								followerUsers = followerUsers,
								followerCount = followerCount,
								ownAccount = ownAccount,
								following = following,
								report = report)
	else:
		reports = db.session.query(Report).filter_by(userReportedID=user.id)

		warnings = db.session.query(Warning).filter_by(userID=user.id)
		warningCheck = db.session.query(Warning).filter_by(userID=user.id).count()
		return render_template('social/user.html',
								user = user,
								subjects = subjects,
								followingUsers = followingUsers,
								followingCount = followingCount,
								followerUsers = followerUsers,
								followerCount = followerCount,
								locationISO = locationISO,
								ownAccount = ownAccount,
								profilePictureForm = profilePictureForm,
								userDetailsForm = userDetailsForm,
								following = following,
								report = report,
								reports = reports,
								warnings = warnings,
								warningCheck = warningCheck)


@social.route('/<string>', methods=['POST', 'GET'])
def share(string):
	first = string[0]
	hash = string[1:]
	if first == 's':
		subject = subjectFromHash(hash)
		return redirect(url_for('subject.subjectList', hash=hash, slug=subject.slug))
	elif first == 't':
		topic = topicFromHash(hash)
		subject = getSubjectByID(topic.subjectID)
		return redirect(url_for('topic.overview', hash=hash, subjectSlug=subject.slug, topicSlug=topic.slug))
	elif first == 'u':
		user = userFromHash(hash)
		return redirect(url_for('social.user', hash=hash))
	else:
		abort(404)


@social.route('/user/<hash>/report', methods=['POST', 'GET'])
def report(hash):

	user = userFromHash(hash)
	userID = user.id

	def reportUser(response, issue):
		if issue.strip() == '':
			response.html('#reportUserForm .errorText', 'Please enter an issue.')
			response.css('#reportUserForm .errorText', 'display', 'block')
			response.css('#reportUserForm .successText', 'display', 'none')
		else:
			addReport(user.id, issue)
			db.session.commit()
			response.html('#reportUserForm .successText', 'Thanks your issue has been received.')
			response.css('#reportUserForm .successText', 'display', 'block')
			response.css('#reportUserForm .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('reportUser', reportUser)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)
		return g.sijax.process_request()

	form = reportForm()

	return render_template('social/report.html',
							user=user,
							form=form)


@social.route('/user/<hash>/warn', methods=['POST', 'GET'])
def warn(hash):

	user = userFromHash(hash)
	userID = user.id

	def warnUser(response, reason):
		if current_user.admin:
			if reason.strip() == '':
				response.html('#warnUserForm .errorText', 'Please enter a reason.')
				response.css('#warnUserForm .errorText', 'display', 'block')
				response.css('#warnUserForm .successText', 'display', 'none')
			else:
				addWarning(user.id, reason)
				db.session.commit()
				response.html('#warnUserForm .successText', 'The user has been warned.')
				response.css('#warnUserForm .successText', 'display', 'block')
				response.css('#warnUserForm .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('warnUser', warnUser)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)
		return g.sijax.process_request()

	form = warnForm()

	return render_template('social/warn.html',
							user=user,
							form=form)


@social.route('/user/<hash>/ban', methods=['POST', 'GET'])
@admin_required
def ban(hash):

	user = userFromHash(hash)
	userID = user.id

	def banUser(response, reason):
		if current_user.admin:
			if reason.strip() == '':
				response.html('#banUserForm .errorText', 'Please enter a reason.')
				response.css('#banUserForm .errorText', 'display', 'block')
				response.css('#banUserForm .successText', 'display', 'none')
			else:
				addBan(user.id, reason)
				db.session.commit()
				response.html('#banUserForm .successText', 'The user has been banned.')
				response.css('#banUserForm .successText', 'display', 'block')
				response.css('#banUserForm .errorText', 'display', 'none')
		response.css('*', 'cursor', 'default')

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('banUser', banUser)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)
		return g.sijax.process_request()

	form = banForm()

	return render_template('social/ban.html',
							user=user,
							form=form)
