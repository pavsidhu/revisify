# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, request, flash
from flask.ext.login import login_user, login_required, current_user
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
import json, requests, urllib, cStringIO

signInOauth = Blueprint('signInOauth', __name__)

google = oauth.remote_app(
	'google',
	consumer_key=app.config['OAUTH_GOOGLE_ID'],
	consumer_secret=app.config['OAUTH_GOOGLE_SECRET'],
	request_token_params={
		'scope': ('https://www.googleapis.com/auth/userinfo.profile' +
				  ' https://www.googleapis.com/auth/userinfo.email' +
				  ' https://www.googleapis.com/auth/plus.login')
	},
	base_url='https://www.googleapis.com/oauth2/v1/',
	request_token_url=None,
	access_token_method='POST',
	access_token_url='https://accounts.google.com/o/oauth2/token',
	authorize_url='https://accounts.google.com/o/oauth2/auth')

facebook = oauth.remote_app(
	'facebook',
	consumer_key=app.config['OAUTH_FACEBOOK_ID'],
	consumer_secret=app.config['OAUTH_FACEBOOK_SECRET'],
	request_token_params={
		'scope': ('public_profile' +
				  ' email' +
				  ' user_location')
	},
	base_url='https://graph.facebook.com',
	request_token_url=None,
	access_token_method='POST',
	access_token_url='/oauth/access_token',
	authorize_url='https://www.facebook.com/dialog/oauth')


@google.tokengetter
def getGoogleOauthToken():
	token = db.session.query(SocialToken).filter_by(userID=current_user.id, provider='g').one()
	return (token.token, '')


@facebook.tokengetter
def getFacebookOauthToken():
	token = db.session.query(SocialToken).filter_by(userID=current_user.id, provider='f').one()
	return (token.token, '')


@signInOauth.route('/authorize/<provider>')
def authorize(provider):
	# If connecting through user settings, prevent a new account being created in callback
	if request.args.get('settings'):
		callback = url_for('signInOauth.authorized', provider=provider, settings=True, _external=True)
	else:
		callback = url_for('signInOauth.authorized', provider=provider, _external=True)

	if provider == 'google':
		return google.authorize(callback=callback)

	elif provider == 'facebook':
		return facebook.authorize(callback=callback)

	else:
		abort(404)


@signInOauth.route('/login/authorized/<provider>')
def authorized(provider):
	# If connecting to social login via the settings menu with existing Revisify account
	try:
		settingsSocialConnect = session['settingsSocialConnect']
		session['settingsSocialConnect'] = None
		redirectURL = url_for('settings.accountSettings')
	except:
		settingsSocialConnect = False
		redirectURL = url_for('account.register')

	if provider == 'google':
		response = google.authorized_response()

		# If OAuth request is denied
		if response is None:
			flash('You didn\'t give Revisify permission to access your Google account. You can create an account with just your email instead.', 'popup')
			return redirect(redirectURL)

		# Receive account data from Google
		userInfoRequest = requests.get(
					'https://www.googleapis.com/plus/v1/people/me',
					verify = False,
					headers={'Authorization': 'OAuth ' + response['access_token']})
		userInfo = json.loads(userInfoRequest.text)

		oauthUser = db.session.query(OAuth).filter_by(socialID=userInfo['id'], provider='G')

		# If row exists with the Google user ID then the user has a Revisify account
		if oauthUser.count() == 1:
			user = User.query.filter_by(id=oauthUser.one().userID).one()
			remember = True

			# Check if the user is logged in i.e if the user connects to social
			# account via the settings but another account is already linked to
			# that social account
			if not current_user.is_anonymous():
				flash('Another Revisify account is already connected to this Google account.', 'popup')
				return redirect(redirectURL)

			signInUser(user, remember)

			# Redirects to last page or main page
			return redirect(request.args.get('next') or url_for('main.index'))

		# If no row exists, then the Google user has no account
		# And if not authorizing through the settings page
		else:
			name = userInfo['displayName']
			socialID = userInfo['id']
			accessToken = response['access_token']

			# Get email from list of emails
			email = None
			for e in userInfo['emails']:
				if e['type'] == 'account':
					email = e['value']

			# if email isn't provided redirect to page to add email address
			if email == None:
				flash('You didn\'t give Revisify permission to access the email associated with your Google account.', 'popup')
				return redirect(redirectURL)

			# if an account already uses that email
			if checkEmail(email):
				if not (settingsSocialConnect and email == current_user.email):
					flash('An account already exists with the email ({}) associated with your Google account.'.format(email), 'popup')
					return redirect(redirectURL)

			if not settingsSocialConnect:
				createAccount(name=name,
							  email=email)

				if not userInfo['image']['isDefault']:
					url = userInfo['image']['url'][:-2] + '270'
					pictureURL = urllib.urlopen(url).read()
					picture = cStringIO.StringIO(pictureURL)

					crop = '0,0,270,270'
					newProfilePicture(picture, crop, oauth=True)

	elif provider == 'facebook':
		response = facebook.authorized_response()

		# If OAuth request is denied
		if response is None:
			flash('You didn\'t give Revisify permission to access your Facebook account. You can create an account with just your email instead!', 'popup')
			return redirect(redirectURL)

		# Receive account data from Facebook
		userInfoRequest = requests.get(
					'https://graph.facebook.com/v2.7/me',
					headers={'Authorization': 'OAuth ' + response['access_token']},
					params={'fields': 'name, email, location{location}'})
		userInfo = json.loads(userInfoRequest.text)

		oauthUser = db.session.query(OAuth).filter_by(socialID=userInfo['id'], provider='F')

		# If row exists with the Facebook user ID then the user has a Revisify account
		if oauthUser.count() == 1:
			user = User.query.filter_by(id=oauthUser.one().userID).one()
			remember = True

			# Check if the user is logged in i.e if the user connects to social
			# account via the settings but another account is already linked to
			# that social account
			if not current_user.is_anonymous():
				flash('Another Revisify account is already connected to this Facebook account.', 'popup')
				return redirect(redirectURL)

			signInUser(user, remember)

			# Redirects to last page or main page
			return redirect(request.args.get('next') or url_for('main.index'))

		# If no row exists, then the Facebook user has no account
		# And if not authorizing through the settings page
		else:
			name = userInfo['name']
			socialID = userInfo['id']
			accessToken = response['access_token']

			# If Facebook user has set their location, get their country in ISO format
			try:
				location = userInfo['location']['location']['country']
				location = getLocationISO(location)
			except:
				location = None

			try:
				email = userInfo['email']

				# if an account already uses that email
				if checkEmail(email):
					if not (settingsSocialConnect and email == current_user.email):
						flash('An account already exists with the email ({}) associated with your Facebook account.'.format(email), 'popup')
						return redirect(redirectURL)

			except:
				# if email isn't provided redirect to page to add email address
				flash('You didn\'t give Revisify permission to access the email associated with your Facebook account.', 'popup')
				return redirect(redirectURL)

			if not settingsSocialConnect:
				createAccount(name=name,
							  email=email,
							  location=location)

				# Check if the user has set a profile picture
				pictureInfoRequest = requests.get(
							'https://graph.facebook.com/v2.7/me/picture',
							headers={'Authorization': 'OAuth ' + response['access_token']},
							params={'width': '270', 'height': '270', 'redirect':False})
				pictureInfo = json.loads(pictureInfoRequest.text)

				if not pictureInfo['data']['is_silhouette']:
					pictureURL = urllib.urlopen(pictureInfo['data']['url']).read()
					picture = cStringIO.StringIO(pictureURL)

					crop = '0,0,270,270'
					newProfilePicture(picture, crop, oauth=True)
	else:
		return abort(404)

	# Add social account connection to database
	oauth = OAuth(
		userID = current_user.id,
		socialID = socialID,
		provider = provider[0].upper(),
		accessToken = accessToken,
		name = name
		)
	db.session.add(oauth)
	db.session.commit()

	if settingsSocialConnect:
		return redirect(redirectURL)
	else:
		return redirect(request.args.get('next') or url_for('main.index'))


@signInOauth.route('/unauthorize/<provider>')
@login_required
def unauthorize(provider):
	if not current_user.password:
		flash('If you disconnect your {} account you will have no other way of signing in. Add a password before disconnecting from {}.'.format(provider.title(), provider.title()), 'popup')
		return redirect(url_for('settings.accountSettings'))

	oauth = db.session.query(OAuth).filter_by(userID=current_user.id, provider=provider[0].upper())

	if oauth.count() == 1:
		oauth.delete()
		db.session.commit()

	return redirect(url_for('settings.accountSettings'))
