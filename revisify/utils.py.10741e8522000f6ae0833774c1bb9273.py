
# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import session, url_for, request, Markup, render_template, redirect, abort, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask.ext.login import current_user, login_user
from itsdangerous import URLSafeTimedSerializer
from urlparse import urlparse, parse_qs
from models import *
from revisify import app
from operator import itemgetter
from functools import wraps
import re, os, requests, random, bleach, json
from werkzeug import secure_filename
from uuid import uuid4
import boto
from boto.s3.key import Key
import boto.s3.connection
import base64
from PIL import Image, ImageFilter
from io import BytesIO
import cStringIO
import calendar
from hashids import Hashids
import flask_sijax
from datetime import datetime, timedelta

ts = URLSafeTimedSerializer(str(app.config['SECRET_KEY']))
hashid = Hashids(salt=app.config['SECRET_KEY'], min_length=6)

# Decorators -----------------------------------------------------------------------------------------------------------------

def activated(f):
	@wraps(f)
	def activatedFunction(*args, **kwargs):
		if current_user.activated:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('confirmation.notConfirmed'))
	return activatedFunction


def admin_required(f):
	@wraps(f)
	def adminFunction(*args, **kwargs):
		if not current_user.is_anonymous():
			if current_user.admin:
				return f(*args, **kwargs)
			else:
				return abort(404)
		else:
			return abort(404)
	return adminFunction


def admin_required(f):
	@wraps(f)
	def adminFunction(*args, **kwargs):
		if not current_user.is_anonymous():
			if current_user.admin:
				return f(*args, **kwargs)
			else:
				return abort(404)
		else:
			return abort(404)
	return adminFunction

# Account Functions ----------------------------------------------------------------------------------------------------------

def createAccount(name, email, password=None, remember=True, location=None):
	email = email.lower()

	if password:
		password = bcrypt.generate_password_hash(password) # Create a hash for the password

	# Add to database
	user = User(name, email, password)
	db.session.add(user)

	# Flush record then create hash
	db.session.flush()
	user.hash = hashid.encode(user.id)
	user.location = location

	db.session.commit()

	activateEmail(user.id) # Sending an email confirmation link

	signInUser(user, remember)


def checkPassword(accountID, password):
	user = db.session.query(User).filter_by(id=accountID).one()
	return bcrypt.check_password_hash(user.password, password)


def checkEmail(email):
	email = email.lower()
	if db.session.query(User).filter_by(email=email).count() == 1:
		return True
	else:
		return False


def signInUser(user, remember):
	login_user(user, remember=remember)
	session.permanent = True


def checkOAuth(provider):
	if provider == 'facebook':
		r = requests.get(
			'https://graph.facebook.com/debug_token',
			headers={'Authorization': 'OAuth ' + session['accessToken']},
			data={'input_token': session['accessToken']}
			)
	elif provider == 'google':
		pass


def socialConnected(provider):
	provider = provider[0].upper()

	social = db.session.query(OAuth).filter_by(userID=current_user.id, provider=provider)

	if social.count() == 1:
		return social.one()
	else:
		return None

# Email Functions ------------------------------------------------------------------------------------------------------------

def activateEmail(id):
	user = db.session.query(User).filter_by(id=id).one()
	token = ts.dumps(user.id, salt='OpoO4Mlr0BO3VQPNroSNndOxafYmhcb04vehKQEf5zjpDD1qckB0P5eprJbc')
	url = url_for('confirmation.confirm', token=token, _external=True)
	html = render_template('email/activate.html', name=user.name, url=url)
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
		  	'to': [user.name + ' <' + user.email + '>'],
			'subject': 'Confirm Your Email',
			'html': html,
			'text': u"""Hi {},

			Please confirm your email by clicking the link below or copy and pasting it into your browser.

			{}

			Follow Revisify on Instagram or Snapchat for study tips, motivation and more.
			You can find us on Facebook and Twitter too.

			Thanks,
			An Automated Email Robot.
			""".format(user.name, url)})


def reactivateEmail(id, newEmail):
	user = db.session.query(User).filter_by(id=id).one()

	tokenString = 'reactivate' + str(user.id) + '+' + newEmail
	token = ts.dumps(tokenString, salt='OpoO4Mlr0BO3VQPNroSNndOxafYmhcb04vehKQEf5zjpDD1qckB0P5eprJbc')
	url = url_for('confirmation.confirm', token=token, _external=True)
	html = render_template('email/activate.html', name=user.name, url=url)
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
		  	'to': [user.name + ' <' + user.email + '>'],
			'subject': 'Confirm Your Email',
			'html': html,
			'text': u"""Hi {},

			Please confirm your email by clicking the link below or copy and pasting it into your browser.

			{}

			Follow Revisify on Instagram or Snapchat for study tips, motivation and more.
			You can find us on Facebook and Twitter too.

			Thanks,
			An Automated Email Robot.
			""".format(user.name, url)})


def welcomeEmail(id):
	user = db.session.query(User).filter_by(id=id, activated=True).one()
	html = render_template('email/welcome.html', name=user.name)
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
			'to': [user.name + ' <' + user.email + '>'],
			'subject': 'Welcome to Revisify',
		  	'html': html,
			'text': u"""Hi {},

			I just want to say hello and welcome you to Revisify! I hope you find Revisify to be incredibly useful for your exams.

			Follow Revisify on Instagram or Snapchat for study tips, motivation and more.
			You can find us on Facebook and Twitter too.

			if you need some help, have some ideas or just want to talk, send us a message (https://revisify.com/contact) and someone from our team will get back to you.

			Happy Studying,
			An Automated Email Robot.
			""".format(user.name)
	})


def passwordReset(id):
	user = db.session.query(User).filter_by(id=id).one()
	token = ts.dumps(user.email, salt='OpoO4Mlr0BO3VQPNroSNndOxafYmhcb04vehKQEf5zjpDD1qckB0P5eprJbc')
	url = url_for('password.reset', token=token, _external=True)
	html = render_template('email/reset.html', name=user.name, url=url)
 	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
			'to': [user.name + ' <' + user.email + '>'],
			'subject': 'Reset Your Password',
			'html': html,
			'text': u"""Hi {},

			Please click the link below to reset your password or copy and paste it into your browser.

			{}

			Follow Revisify on Instagram or Snapchat for study tips, motivation and more.
			You can find us on Facebook and Twitter too.

			Thanks,
			An Automated Email Robot.
			""".format(user.name, url)
	})


def warnEmail(userID, reason):
	name = getName(userID)
	email = getEmail(userID)
	html = render_template('email/warn.html', name=name, reason=reason)
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
			'to': [name + ' <' + email + '>'],
			'subject': 'You Have Violated Our Terms',
			'html': html,
			'text': u"""Hi {},

  			It has come to our attention that your account has been violating Revisify's Terms of Service (http://revisify.com/terms-of-service).

  			{}

			The content we found to be inappropriate has been removed. Please be aware that in the event of another violation, your account will be banned.
			If you believe our decision is an error, please contact us (https://revisify.com/contact).

  			Thanks,
  			Revisify.
			""".format(name, reason)
	})


def banEmail(userID, reason):
	name = getName(userID)
	email = getEmail(userID)
	html = render_template('email/ban.html', name=name, reason=reason)
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': app.config['MAIL_DEFAULT_SENDER'],
			'to': [name + ' <' + email + '>'],
			'subject': 'Your Account Has Been Suspended',
			'html': html,
			'text': u"""Hi {},

  			It has come to our attention that your account has violated Revisify's Terms of Service (http://revisify.com/terms-of-service) for the second time.

  			{}

			As a result of violating our Terms of Service, your account has been suspended. You will no longer be able to sign in to your account or access it by any other means.

			If you believe our decision is an error, please contact us (https://revisify.com/contact).

  			Thanks,
  			Revisify.
  			""".format(name, reason)
	})


def reportEmail(userID, userReportedID, issue):
	# Get reported details
	reportedUser = db.session.query(User).filter_by(id=userReportedID).one()

	if userID == None:
		reporterName = 'Anonymous'
		reporterEmail = 'anonymous-report@revisify.com'
	else:
		# Get reporter's details
		reporterUser = db.session.query(User).filter_by(id=userID).one()
		reporterName = reporterUser.name
		reporterEmail = reporterUser.email

	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': reporterName + ' <' + reporterEmail + '>',
			'to': ['support@revisify.com'],
			'subject': '{} Has Been Reported'.format(reportedUser.name),
 			'text': u"""{} has been reported by {}: {}
			Take action: http://revisify.com/admin/reports
			""".format(reportedUser.name, reporterName, issue)
	})


def contactEmail(name, email, message):
	return requests.post(
		'https://api.mailgun.net/v3/revisify.com/messages',
		auth=('api', app.config['MAIL_SECRET_KEY']),
		data={
			'from': email,
			'to': ['support@revisify.com'],
			'subject': '{} Has Contacted Revisify Support'.format(name),
			'text': message
	})

# Social Functions  ----------------------------------------------------------------------------------------------------------

def getUser(id):
	return db.session.query(User).filter_by(id=id).one()


def followedUsers(userID):
	userFollowing = db.session.query(Follow).filter_by(follower=userID)
	following = []
	for userFollow in userFollowing:
		id = userFollow.following
		user = db.session.query(User).filter_by(id=id).one()
		if user.profile:
			following.append({
				'id': id,
				'name': user.name,
				'hash': user.hash,
				'icon': user.profilePicture
			})

	# Return sorted list in order of name
	return sorted(following, key=itemgetter('name'))


def userFollowers(userID):
	getFollowers = db.session.query(Follow).filter_by(following=userID)
	followers = []
	for follower in getFollowers:
		id = follower.follower
		user = db.session.query(User).filter_by(id=id).one()
		if user.profile:
			followers.append({
				'id': id,
				'name': user.name,
				'hash': user.hash,
				'icon': user.profilePicture
			})

	# Return sorted list in order of name
	return sorted(followers, key=itemgetter('name'))


def checkFollow(follower, following):
	if db.session.query(Follow).filter_by(follower=follower, following=following).count() == 1:
		return True
	else:
		return False


def getName(accountID):
	return db.session.query(User.name).filter_by(id=accountID).one()[0]


def getEmail(accountID):
	return db.session.query(User.email).filter_by(id=accountID).one()[0]


def checkWarn(userID):
	if db.session.query(Warning).filter_by(userID=userID).first():
		return True
	else:
		return False


def addReport(userReportedID, issue):
	# If user is logged in or not
	if current_user.is_anonymous():
		user = None
	else:
		user = current_user.id

	# Add report to database
	report = Report(user, userReportedID, issue)
	db.session.add(report)
	db.session.commit()

	# Send email to admins
	reportEmail(user, userReportedID, issue)


def addWarning(userID, reason):
	# Add warning to database
	warning = Warning(userID, reason)
	db.session.add(warning)
	db.session.commit()

	# Send email to warned user
	warnEmail(userID, reason)


def addBan(userID, reason):
	# Add ban to database
	ban = Ban(userID)
	db.session.add(ban)

	# Set user's profile to private to hide from other users
	user = loadUser(userID)
	user.profile = False

	# Remove followers
	db.session.query(Follow).filter_by(follower=userID).delete()
	db.session.query(Follow).filter_by(following=userID).delete()

	db.session.commit()

	# Send email to banned user
	banEmail(userID, reason)

# Hash Functions -------------------------------------------------------------------------------------------------------------

def hashID(id):
	return hashid.encode(id)


def userFromHash(hash):
	try:
		id = hashid.decode(hash)
		return db.session.query(User).filter_by(id=id).one()
	except:
		abort(404)


def subjectFromHash(hash):
	try:
		id = hashid.decode(hash)
		return db.session.query(Subject).filter_by(id=id).one()
	except:
		abort(404)


def topicFromHash(hash):
	try:
		id = hashid.decode(hash)
		return db.session.query(Topic).filter_by(id=id).one()
	except:
		abort(404)

# Subject/Topic Functions ----------------------------------------------------------------------------------------------------

def getSubjectByAccount(accountID):
	return db.session.query(Subject).filter_by(accountID=accountID).order_by(Subject.name).all()


def getSubjectByID(id):
	return db.session.query(Subject).filter_by(id=id).one()


def getTopicByID(id):
	return db.session.query(Topic).filter_by(id=id).one()


def getSubjectNames(accountID):
	query = db.session.query(Subject).filter_by(accountID=accountID).all()
	subjectList = []
	for subject in query:
		subjectList.append(subject.name.lower())
	return subjectList


def getTopicNames(accountID, subject):
	query = db.session.query(Topic).join(Subject).filter(and_(Subject.name==subject, Subject.accountID==accountID)).all()
	topicList = []
	for topic in query:
		topicList.append(topic.name.lower())
	return topicList


def getTopics(subjectID):
	query = db.session.query(Topic).join(Subject).filter(and_(Subject.id==subjectID))

	color = getColor(subjectID)

	topics = []
	for topic in query:
		if current_user.is_anonymous():
			percentage = None
		else:
			percentage = getTopicPercentage(topic.id)

		contentLink = url_for('topic.overview',
							  hash=topic.hash,
							  subjectSlug=topic.subject.slug,
							  topicSlug=topic.slug
							  )
		shareLink = url_for('social.share',
							string = 't' + topic.hash,
							_external = True
							)
		topics.append({
			'id': topic.id,
			'name': topic.name,
			'hash': topic.hash,
			'slug': topic.slug,
			'percentage': percentage,
			'contentLink': contentLink,
			'shareLink': shareLink,
			'textcolor': color['text'],
			'iconcolor': color['icon']
		})

		topics = sorted(topics, key=lambda k: k['name'])
	return topics


def getSubjectPercentage(subjectID):
	if current_user.is_anonymous():
		return None

	subjectPercentage = 0.0
	topics = getTopics(subjectID)

	# If the subject has no topics return nothing
	if not topics:
		return 0

	for topic in topics:
		subjectPercentage += getTopicPercentage(topic['id'])

	return int(subjectPercentage / len(topics))


def getTopicPercentage(topicID):
	if current_user.is_anonymous():
		return None

	topicPercentage = 0.0

	# Iterate through results of the topic
	topicResult = getTopicResult(topicID)[0:3]

	if topicResult:
		# Add total results for that topic
		for result in topicResult:
			topicPercentage += float(result.percentage)

		# Divide by number of results available max is 3
		return int(topicPercentage / len(topicResult))
	else:
		# Return nothing is there are no results available
		return 0


def getTopicResult(topicID):
	if current_user.is_anonymous():
		return None
	else:
		return db.session.query(Result).filter_by(topicID=topicID, accountID=current_user.id).order_by(Result.id.desc()).all()

# Slug Functions --------------------------------------------------------------------------------------------------------------

def uniqueSubjectSlug(name, uids):
	if db.session.query(Subject).filter_by(slug=name, accountID=current_user.id).count() == 0:
		return True # If 0 it is unique
	else:
		return False # If more than 0 it is not unique

def uniqueTopicSlug(name, uids):
	if db.session.query(Topic).filter_by(slug=name, subjectID=session['newTopicSubjectID']).join(Subject).filter(Subject.accountID==current_user.id).count() == 0:
		return True # If 0 it is unique
	else:
		return False # If more than 0 it is not unique

subjectSlug = UniqueSlugify(unique_check=uniqueSubjectSlug, to_lower=True)
topicSlug = UniqueSlugify(unique_check=uniqueTopicSlug, to_lower=True)

# Gamification Functions ------------------------------------------------------------------------------------------------------

def getSundayDate():
	date = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
	return date.date()


def getWeeklyGoal(userID):
	goal = db.session.query(WeeklyGoal).filter_by(userID=userID, date=getSundayDate())

	if goal.count() == 1:
		return goal.one()
	else:
		return None


def getWeeklyGoalProgress(userID):
	goal = getWeeklyGoal(userID)
	if goal:
		return goal.progress
	else:
		return 0


def getStudyStreakResults(userID):
	query = db.session.query(Result.date).filter_by(accountID=userID).order_by(Result.date.desc())
	results = []

	for i, result in enumerate(query):
		if i == 0:
			results.append(str(result.date))
			continue

		# Check if date of result is the same as the last one or the day before the last one
		if result.date == query[i-1][0] or result.date == query[i-1][0] - timedelta(days=1):
			results.append(str(result.date))
		else:
			break

	return results

# Profile Picture Functions --------------------------------------------------------------------------------------------------

def newProfilePicture(picture, crop, oauth=False):
	if not oauth:
		if not imageFiletype(picture.filename):
			return

	# Get image and open with PIL
	picture = Image.open(picture)

	# If picture is from Facebook, resize image so that it's 270x270
	if oauth:
		picture = picture.resize((270, 270), Image.ANTIALIAS)

	# Get crop dimensions
	crop = crop.split(',')
	left = int(crop[0])
	top = int(crop[1])
	right = int(crop[2])
	bottom = int(crop[3])
	cropped = picture.crop((left, top, right, bottom)) # Crop picture

	# Small profile picture
	smallProfilePicture = cropped.resize((80, 80), Image.ANTIALIAS).convert('RGB')
	smallProfilePictureBuffer = cStringIO.StringIO()
	smallProfilePicture.save(smallProfilePictureBuffer, format='JPEG', optimize=True, quality=80)
	small = base64.b64encode(smallProfilePictureBuffer.getvalue())

	# Large profile picture
	largeProfilePicture = cropped.resize((270, 270), Image.ANTIALIAS).convert('RGB')
	largeProfilePictureBuffer = cStringIO.StringIO()
	largeProfilePicture.save(largeProfilePictureBuffer, format='JPEG', optimize=True, quality=100)
	large = base64.b64encode(largeProfilePictureBuffer.getvalue())

	# Blurred cover profile picture
	coverProfilePicture = cropped.resize((500, 500), Image.ANTIALIAS).convert('RGB').filter(ImageFilter.GaussianBlur(10))
	coverProfilePictureBuffer = cStringIO.StringIO()
	coverProfilePicture.save(coverProfilePictureBuffer, format='JPEG', optimize=True, quality=100)
	cover = base64.b64encode(coverProfilePictureBuffer.getvalue())

	# Update picture value in database
	current_user.picture = uuid4().hex
	db.session.commit()

	# Connect to S3 bucket
	connection = boto.s3.connect_to_region(
		'us-east-1',
		aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
		aws_secret_access_key = app.config['AWS_SECRET_ACCESS_KEY'],
		calling_format = boto.s3.connection.OrdinaryCallingFormat()
	)

	bucket = connection.get_bucket('data.revisify.com', validate=False)

	# Delete existing user folder which contains the profile picture
	for key in bucket.list(prefix=str(current_user.id) + '/'):
		key.delete()

	# Create key and upload small profile picture
	smallKey = bucket.new_key('/'.join([str(current_user.id), current_user.picture + '_80x80.jpeg']))
	smallKey.set_contents_from_string(base64.b64decode(small))
	smallKey.set_acl('public-read') # Set permissions to be publicly accessable

	# Create key and upload large profile picture
	largeKey = bucket.new_key('/'.join([str(current_user.id), current_user.picture + '_270x270.jpeg']))
	largeKey.set_contents_from_string(base64.b64decode(large))
	largeKey.set_acl('public-read')

	# Create key and upload cover image
	coverKey = bucket.new_key('/'.join([str(current_user.id), current_user.picture + '_cover.jpeg']))
	coverKey.set_contents_from_string(base64.b64decode(cover))
	coverKey.set_acl('public-read')


def imageFiletype(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg'])

# Color Functions ------------------------------------------------------------------------------------------------------------

def getColor(subjectID):
	c = db.session.query(Subject).filter_by(id=subjectID).one().color
	if c == 0: # Red
		return {
			'id': '0',
			'text': '#FFEBEE',
			'icon': '#C62828',
			'bg': '#B71C1C',
			'nav': '#911616'
		}
	elif c == 1: # Pink
		return {
			'id': '1',
			'text': '#FCE4EC',
			'icon': '#C2185B',
			'bg': '#AD1457',
			'nav': '#96114C'
		}
	elif c == 2: # Purple
		return {
			'id': '2',
			'text': '#EDE7F6',
			'icon': '#5E35B1',
			'bg': '#512DA8',
			'nav': '#462791'
		}
	elif c == 3: # Blue
		return {
			'id': '3',
			'text': '#E3F2FD',
			'icon': '#1976D2',
			'bg': '#1565C0',
			'nav': '#1255A1'
		}
	elif c == 4: # Cyan
		return {
			'id': '4',
			'text': '#E0F7FA',
			'icon': '#00BCD4',
			'bg': '#00ACC1',
			'nav': '#0097A7'
		}
	elif c == 5: # Teal
		return {
			'id': '5',
			'text': '#E0F2F1',
			'icon': '#009688',
			'bg': '#00796B',
			'nav': '#00695C'
		}
	elif c == 6: # Green
		return {
			'id': '6',
			'text': '#F1F8E9',
			'icon': '#7CB342',
			'bg': '#689F38',
			'nav': '#558B2F'
		}
	elif c == 7: # Lime
		return {
			'id': '7',
			'text': '#F9FBE7',
			'icon': '#C0CA33',
			'bg': '#AFB42B',
			'nav': '#9E9D24'
		}
	elif c == 8: # Orange
		return {
			'id': '8',
			'text': '#FBE9E7',
			'icon': '#FF5722',
			'bg': '#D84315',
			'nav': '#BF360C'
		}
	elif c == 9: # Brown
		return {
			'id': '9',
			'text': '#EFEBE9',
			'icon': '#6D4C41',
			'bg': '#5D4037',
			'nav': '#4E342E'
		}


def getColorByNumber(number):
	if number == 0: # Red
		return {
			'id': '0',
			'text': '#FFEBEE',
			'icon': '#C62828',
			'bg': '#B71C1C',
			'nav': '#911616'
		}
	elif number == 1: # Pink
		return {
			'id': '1',
			'text': '#FCE4EC',
			'icon': '#C2185B',
			'bg': '#AD1457',
			'nav': '#96114C'
		}
	elif number == 2: # Purple
		return {
			'id': '2',
			'text': '#EDE7F6',
			'icon': '#5E35B1',
			'bg': '#512DA8',
			'nav': '#462791'
		}
	elif number == 3: # Blue
		return {
			'id': '3',
			'text': '#E3F2FD',
			'icon': '#1976D2',
			'bg': '#1565C0',
			'nav': '#1255A1'
		}
	elif number == 4: # Cyan
		return {
			'id': '4',
			'text': '#E0F7FA',
			'icon': '#00BCD4',
			'bg': '#00ACC1',
			'nav': '#0097A7'
		}
	elif number == 5: # Teal
		return {
			'id': '5',
			'text': '#E0F2F1',
			'icon': '#009688',
			'bg': '#00796B',
			'nav': '#00695C'
		}
	elif number == 6: # Green
		return {
			'id': '6',
			'text': '#F1F8E9',
			'icon': '#7CB342',
			'bg': '#689F38',
			'nav': '#558B2F'
		}
	elif number == 7: # Lime
		return {
			'id': '7',
			'text': '#F9FBE7',
			'icon': '#C0CA33',
			'bg': '#AFB42B',
			'nav': '#9E9D24'
		}
	elif number == 8: # Orange
		return {
			'id': '8',
			'text': '#FBE9E7',
			'icon': '#FF5722',
			'bg': '#D84315',
			'nav': '#BF360C'
		}
	elif number == 9: # Brown
		return {
			'id': '9',
			'text': '#EFEBE9',
			'icon': '#6D4C41',
			'bg': '#5D4037',
			'nav': '#4E342E'
		}


def hexToRGB(value):
	value = value.lstrip('#')
	length = len(value)
	return tuple(int(value[i:i+length/3], 16) for i in range(0, length, length/3))

# Other Functions ------------------------------------------------------------------------------------------------------------

def getLocation(iso):
	locations = [('AF', 'Afghanistan'),
		('AF', 'Afghanistan'),
		('AX', 'Aland Islands'),
		('AL', 'Albania'),
		('DZ', 'Algeria'),
		('AS', 'American Samoa'),
		('AD', 'Andorra'),
		('AO', 'Angola'),
		('AI', 'Anguilla'),
		('AQ', 'Antarctica'),
		('AG', 'Antigua and Barbuda'),
		('AR', 'Argentina'),
		('AM', 'Armenia'),
		('AW', 'Aruba'),
		('AU', 'Australia'),
		('AT', 'Austria'),
		('AZ', 'Azerbaijan'),
		('BS', 'Bahamas'),
		('BH', 'Bahrain'),
		('BD', 'Bangladesh'),
		('BB', 'Barbados'),
		('BY', 'Belarus'),
		('BE', 'Belgium'),
		('BZ', 'Belize'),
		('BJ', 'Benin'),
		('BM', 'Bermuda'),
		('BT', 'Bhutan'),
		('BO', 'Bolivia'),
		('BQ', 'Bonaire, Sint Eustatius and Saba'),
		('BA', 'Bosnia and Herzegovina'),
		('BW', 'Botswana'),
		('BV', 'Bouvet Island'),
		('BR', 'Brazil'),
		('IO', 'British Indian Ocean Territory'),
		('BN', 'Brunei'),
		('BG', 'Bulgaria'),
		('BF', 'Burkina Faso'),
		('BI', 'Burundi'),
		('KH', 'Cambodia'),
		('CM', 'Cameroon'),
		('CA', 'Canada'),
		('CV', 'Cape Verde'),
		('KY', 'Cayman Islands'),
		('CF', 'Central African Republic'),
		('TD', 'Chad'),
		('CL', 'Chile'),
		('CN', 'China'),
		('CX', 'Christmas Island'),
		('CC', 'Cocos (Keeling) Islands'),
		('CO', 'Colombia'),
		('KM', 'Comoros'),
		('CG', 'Republic of Congo'),
		('CD', 'Democratic Republic of Congo'),
		('CK', 'Cook Islands'),
		('CR', 'Costa Rica'),
		('CI', 'Cote d\'Ivoire'),
		('HR', 'Croatia'),
		('CU', 'Cuba'),
		('CW', 'Curacao'),
		('CY', 'Cyprus'),
		('CZ', 'Czech Republic'),
		('DK', 'Denmark'),
		('DJ', 'Djibouti'),
		('DM', 'Dominica'),
		('DO', 'Dominican Republic'),
		('EC', 'Ecuador'),
		('EG', 'Egypt'),
		('SV', 'El Salvador'),
		('GQ', 'Equatorial Guinea'),
		('ER', 'Eritrea'),
		('EE', 'Estonia'),
		('ET', 'Ethiopia'),
		('FK', 'Falkland Islands'),
		('FO', 'Faroe Islands'),
		('FJ', 'Fiji'),
		('FI', 'Finland'),
		('FR', 'France'),
		('GF', 'French Guiana'),
		('PF', 'French Polynesia'),
		('TF', 'French Southern Territories'),
		('GA', 'Gabon'),
		('GM', 'Gambia'),
		('GE', 'Georgia'),
		('DE', 'Germany'),
		('GH', 'Ghana'),
		('GI', 'Gibraltar'),
		('GR', 'Greece'),
		('GL', 'Greenland'),
		('GD', 'Grenada'),
		('GP', 'Guadeloupe'),
		('GU', 'Guam'),
		('GT', 'Guatemala'),
		('GG', 'Guernsey'),
		('GN', 'Guinea'),
		('GW', 'Guinea-Bissau'),
		('GY', 'Guyana'),
		('HT', 'Haiti'),
		('HM', 'Heard and McDonald Islands'),
		('VA', 'Vatican City'),
		('HN', 'Honduras'),
		('HK', 'Hong Kong'),
		('HU', 'Hungary'),
		('IS', 'Iceland'),
		('IN', 'India'),
		('ID', 'Indonesia'),
		('IR', 'Iran'),
		('IQ', 'Iraq'),
		('IE', 'Ireland'),
		('IM', 'Isle of Man'),
		('IL', 'Israel'),
		('IT', 'Italy'),
		('JM', 'Jamaica'),
		('JP', 'Japan'),
		('JE', 'Jersey'),
		('JO', 'Jordan'),
		('KZ', 'Kazakhstan'),
		('KE', 'Kenya'),
		('KI', 'Kiribati'),
		('KP', 'North Korea'),
		('KR', 'South Korea'),
		('KW', 'Kuwait'),
		('KG', 'Kyrgyzstan'),
		('LA', 'Laos'),
		('LV', 'Latvia'),
		('LB', 'Lebanon'),
		('LS', 'Lesotho'),
		('LR', 'Liberia'),
		('LY', 'Libya'),
		('LI', 'Liechtenstein'),
		('LT', 'Lithuania'),
		('LU', 'Luxembourg'),
		('MO', 'Macao'),
		('MK', 'Macedonia'),
		('MG', 'Madagascar'),
		('MW', 'Malawi'),
		('MY', 'Malaysia'),
		('MV', 'Maldives'),
		('ML', 'Mali'),
		('MT', 'Malta'),
		('MH', 'Marshall Islands'),
		('MQ', 'Martinique'),
		('MR', 'Mauritania'),
		('MU', 'Mauritius'),
		('YT', 'Mayotte'),
		('MX', 'Mexico'),
		('FM', 'Micronesia'),
		('MD', 'Moldova'),
		('MC', 'Monaco'),
		('MN', 'Mongolia'),
		('ME', 'Montenegro'),
		('MS', 'Montserrat'),
		('MA', 'Morocco'),
		('MZ', 'Mozambique'),
		('MM', 'Myanmar'),
		('NA', 'Namibia'),
		('NR', 'Nauru'),
		('NP', 'Nepal'),
		('NL', 'Netherlands'),
		('NC', 'New Caledonia'),
		('NZ', 'New Zealand'),
		('NI', 'Nicaragua'),
		('NE', 'Niger'),
		('NG', 'Nigeria'),
		('NU', 'Niue'),
		('NF', 'Norfolk Island'),
		('MP', 'Northern Mariana Islands'),
		('NO', 'Norway'),
		('OM', 'Oman'),
		('PK', 'Pakistan'),
		('PW', 'Palau'),
		('PS', 'Palestinian Territory, Occupied'),
		('PA', 'Panama'),
		('PG', 'Papua New Guinea'),
		('PY', 'Paraguay'),
		('PE', 'Peru'),
		('PH', 'Philippines'),
		('PN', 'Pitcairn'),
		('PL', 'Poland'),
		('PT', 'Portugal'),
		('PR', 'Puerto Rico'),
		('QA', 'Qatar'),
		('RE', 'Reunion'),
		('RO', 'Romania'),
		('RU', 'Russian Federation'),
		('RW', 'Rwanda'),
		('BL', 'Saint Barthelemy'),
		('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
		('KN', 'Saint Kitts and Nevis'),
		('LC', 'Saint Lucia'),
		('MF', 'Saint Martin'),
		('PM', 'Saint Pierre and Miquelon'),
		('VC', 'Saint Vincent and the Grenadines'),
		('WS', 'Samoa'),
		('SM', 'San Marino'),
		('ST', 'Sao Tome and Principe'),
		('SA', 'Saudi Arabia'),
		('SN', 'Senegal'),
		('RS', 'Serbia'),
		('SC', 'Seychelles'),
		('SL', 'Sierra Leone'),
		('SG', 'Singapore'),
		('SX', 'Sint Maarten'),
		('SK', 'Slovakia'),
		('SI', 'Slovenia'),
		('SB', 'Solomon Islands'),
		('SO', 'Somalia'),
		('ZA', 'South Africa'),
		('GS', 'South Georgia and the South Sandwich Islands'),
		('SS', 'South Sudan'),
		('ES', 'Spain'),
		('LK', 'Sri Lanka'),
		('SD', 'Sudan'),
		('SR', 'Suriname'),
		('SJ', 'Svalbard and Jan Mayen'),
		('SZ', 'Swaziland'),
		('SE', 'Sweden'),
		('CH', 'Switzerland'),
		('SY', 'Syrian Arab Republic'),
		('TW', 'Taiwan'),
		('TJ', 'Tajikistan'),
		('TZ', 'Tanzania'),
		('TH', 'Thailand'),
		('TL', 'Timor-Leste'),
		('TG', 'Togo'),
		('TK', 'Tokelau'),
		('TO', 'Tonga'),
		('TT', 'Trinidad and Tobago'),
		('TN', 'Tunisia'),
		('TR', 'Turkey'),
		('TM', 'Turkmenistan'),
		('TC', 'Turks and Caicos Islands'),
		('TV', 'Tuvalu'),
		('UG', 'Uganda'),
		('UA', 'Ukraine'),
		('AE', 'United Arab Emirates'),
		('GB', 'United Kingdom'),
		('US', 'United States'),
		('UM', 'United States Minor Outlying Islands'),
		('UY', 'Uruguay'),
		('UZ', 'Uzbekistan'),
		('VU', 'Vanuatu'),
		('VE', 'Venezuela'),
		('VN', 'Vietnam'),
		('VG', 'Virgin Islands, British'),
		('VI', 'Virgin Islands, U.S.'),
		('WF', 'Wallis and Futuna'),
		('EH', 'Western Sahara'),
		('YE', 'Yemen'),
		('ZM', 'Zambia'),
		('ZW', 'Zimbabwe')]
	for l in locations:
		if l[0] == iso:
			return l[1]


def getLocationISO(location):
	locations = [('AF', 'Afghanistan'),
		('AF', 'Afghanistan'),
		('AX', 'Aland Islands'),
		('AL', 'Albania'),
		('DZ', 'Algeria'),
		('AS', 'American Samoa'),
		('AD', 'Andorra'),
		('AO', 'Angola'),
		('AI', 'Anguilla'),
		('AQ', 'Antarctica'),
		('AG', 'Antigua and Barbuda'),
		('AR', 'Argentina'),
		('AM', 'Armenia'),
		('AW', 'Aruba'),
		('AU', 'Australia'),
		('AT', 'Austria'),
		('AZ', 'Azerbaijan'),
		('BS', 'Bahamas'),
		('BH', 'Bahrain'),
		('BD', 'Bangladesh'),
		('BB', 'Barbados'),
		('BY', 'Belarus'),
		('BE', 'Belgium'),
		('BZ', 'Belize'),
		('BJ', 'Benin'),
		('BM', 'Bermuda'),
		('BT', 'Bhutan'),
		('BO', 'Bolivia'),
		('BQ', 'Bonaire, Sint Eustatius and Saba'),
		('BA', 'Bosnia and Herzegovina'),
		('BW', 'Botswana'),
		('BV', 'Bouvet Island'),
		('BR', 'Brazil'),
		('IO', 'British Indian Ocean Territory'),
		('BN', 'Brunei'),
		('BG', 'Bulgaria'),
		('BF', 'Burkina Faso'),
		('BI', 'Burundi'),
		('KH', 'Cambodia'),
		('CM', 'Cameroon'),
		('CA', 'Canada'),
		('CV', 'Cape Verde'),
		('KY', 'Cayman Islands'),
		('CF', 'Central African Republic'),
		('TD', 'Chad'),
		('CL', 'Chile'),
		('CN', 'China'),
		('CX', 'Christmas Island'),
		('CC', 'Cocos (Keeling) Islands'),
		('CO', 'Colombia'),
		('KM', 'Comoros'),
		('CG', 'Republic of Congo'),
		('CD', 'Democratic Republic of Congo'),
		('CK', 'Cook Islands'),
		('CR', 'Costa Rica'),
		('CI', 'Cote d\'Ivoire'),
		('HR', 'Croatia'),
		('CU', 'Cuba'),
		('CW', 'Curacao'),
		('CY', 'Cyprus'),
		('CZ', 'Czech Republic'),
		('DK', 'Denmark'),
		('DJ', 'Djibouti'),
		('DM', 'Dominica'),
		('DO', 'Dominican Republic'),
		('EC', 'Ecuador'),
		('EG', 'Egypt'),
		('SV', 'El Salvador'),
		('GQ', 'Equatorial Guinea'),
		('ER', 'Eritrea'),
		('EE', 'Estonia'),
		('ET', 'Ethiopia'),
		('FK', 'Falkland Islands'),
		('FO', 'Faroe Islands'),
		('FJ', 'Fiji'),
		('FI', 'Finland'),
		('FR', 'France'),
		('GF', 'French Guiana'),
		('PF', 'French Polynesia'),
		('TF', 'French Southern Territories'),
		('GA', 'Gabon'),
		('GM', 'Gambia'),
		('GE', 'Georgia'),
		('DE', 'Germany'),
		('GH', 'Ghana'),
		('GI', 'Gibraltar'),
		('GR', 'Greece'),
		('GL', 'Greenland'),
		('GD', 'Grenada'),
		('GP', 'Guadeloupe'),
		('GU', 'Guam'),
		('GT', 'Guatemala'),
		('GG', 'Guernsey'),
		('GN', 'Guinea'),
		('GW', 'Guinea-Bissau'),
		('GY', 'Guyana'),
		('HT', 'Haiti'),
		('HM', 'Heard and McDonald Islands'),
		('VA', 'Vatican City'),
		('HN', 'Honduras'),
		('HK', 'Hong Kong'),
		('HU', 'Hungary'),
		('IS', 'Iceland'),
		('IN', 'India'),
		('ID', 'Indonesia'),
		('IR', 'Iran'),
		('IQ', 'Iraq'),
		('IE', 'Ireland'),
		('IM', 'Isle of Man'),
		('IL', 'Israel'),
		('IT', 'Italy'),
		('JM', 'Jamaica'),
		('JP', 'Japan'),
		('JE', 'Jersey'),
		('JO', 'Jordan'),
		('KZ', 'Kazakhstan'),
		('KE', 'Kenya'),
		('KI', 'Kiribati'),
		('KP', 'North Korea'),
		('KR', 'South Korea'),
		('KW', 'Kuwait'),
		('KG', 'Kyrgyzstan'),
		('LA', 'Laos'),
		('LV', 'Latvia'),
		('LB', 'Lebanon'),
		('LS', 'Lesotho'),
		('LR', 'Liberia'),
		('LY', 'Libya'),
		('LI', 'Liechtenstein'),
		('LT', 'Lithuania'),
		('LU', 'Luxembourg'),
		('MO', 'Macao'),
		('MK', 'Macedonia'),
		('MG', 'Madagascar'),
		('MW', 'Malawi'),
		('MY', 'Malaysia'),
		('MV', 'Maldives'),
		('ML', 'Mali'),
		('MT', 'Malta'),
		('MH', 'Marshall Islands'),
		('MQ', 'Martinique'),
		('MR', 'Mauritania'),
		('MU', 'Mauritius'),
		('YT', 'Mayotte'),
		('MX', 'Mexico'),
		('FM', 'Micronesia'),
		('MD', 'Moldova'),
		('MC', 'Monaco'),
		('MN', 'Mongolia'),
		('ME', 'Montenegro'),
		('MS', 'Montserrat'),
		('MA', 'Morocco'),
		('MZ', 'Mozambique'),
		('MM', 'Myanmar'),
		('NA', 'Namibia'),
		('NR', 'Nauru'),
		('NP', 'Nepal'),
		('NL', 'Netherlands'),
		('NC', 'New Caledonia'),
		('NZ', 'New Zealand'),
		('NI', 'Nicaragua'),
		('NE', 'Niger'),
		('NG', 'Nigeria'),
		('NU', 'Niue'),
		('NF', 'Norfolk Island'),
		('MP', 'Northern Mariana Islands'),
		('NO', 'Norway'),
		('OM', 'Oman'),
		('PK', 'Pakistan'),
		('PW', 'Palau'),
		('PS', 'Palestinian Territory, Occupied'),
		('PA', 'Panama'),
		('PG', 'Papua New Guinea'),
		('PY', 'Paraguay'),
		('PE', 'Peru'),
		('PH', 'Philippines'),
		('PN', 'Pitcairn'),
		('PL', 'Poland'),
		('PT', 'Portugal'),
		('PR', 'Puerto Rico'),
		('QA', 'Qatar'),
		('RE', 'Reunion'),
		('RO', 'Romania'),
		('RU', 'Russian Federation'),
		('RW', 'Rwanda'),
		('BL', 'Saint Barthelemy'),
		('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
		('KN', 'Saint Kitts and Nevis'),
		('LC', 'Saint Lucia'),
		('MF', 'Saint Martin'),
		('PM', 'Saint Pierre and Miquelon'),
		('VC', 'Saint Vincent and the Grenadines'),
		('WS', 'Samoa'),
		('SM', 'San Marino'),
		('ST', 'Sao Tome and Principe'),
		('SA', 'Saudi Arabia'),
		('SN', 'Senegal'),
		('RS', 'Serbia'),
		('SC', 'Seychelles'),
		('SL', 'Sierra Leone'),
		('SG', 'Singapore'),
		('SX', 'Sint Maarten'),
		('SK', 'Slovakia'),
		('SI', 'Slovenia'),
		('SB', 'Solomon Islands'),
		('SO', 'Somalia'),
		('ZA', 'South Africa'),
		('GS', 'South Georgia and the South Sandwich Islands'),
		('SS', 'South Sudan'),
		('ES', 'Spain'),
		('LK', 'Sri Lanka'),
		('SD', 'Sudan'),
		('SR', 'Suriname'),
		('SJ', 'Svalbard and Jan Mayen'),
		('SZ', 'Swaziland'),
		('SE', 'Sweden'),
		('CH', 'Switzerland'),
		('SY', 'Syrian Arab Republic'),
		('TW', 'Taiwan'),
		('TJ', 'Tajikistan'),
		('TZ', 'Tanzania'),
		('TH', 'Thailand'),
		('TL', 'Timor-Leste'),
		('TG', 'Togo'),
		('TK', 'Tokelau'),
		('TO', 'Tonga'),
		('TT', 'Trinidad and Tobago'),
		('TN', 'Tunisia'),
		('TR', 'Turkey'),
		('TM', 'Turkmenistan'),
		('TC', 'Turks and Caicos Islands'),
		('TV', 'Tuvalu'),
		('UG', 'Uganda'),
		('UA', 'Ukraine'),
		('AE', 'United Arab Emirates'),
		('GB', 'United Kingdom'),
		('US', 'United States'),
		('UM', 'United States Minor Outlying Islands'),
		('UY', 'Uruguay'),
		('UZ', 'Uzbekistan'),
		('VU', 'Vanuatu'),
		('VE', 'Venezuela'),
		('VN', 'Vietnam'),
		('VG', 'Virgin Islands, British'),
		('VI', 'Virgin Islands, U.S.'),
		('WF', 'Wallis and Futuna'),
		('EH', 'Western Sahara'),
		('YE', 'Yemen'),
		('ZM', 'Zambia'),
		('ZW', 'Zimbabwe')]
	for l in locations:
		if l[1] == location:
			return l[0]

# Global AJAX Functions ------------------------------------------------------------------------------------------------------
# These functions are put here since they are registered in @app.after_request and MUST be registered in every view which uses
# Sijax in any way.

def confirmEmail(response):
	if current_user.activated == False:
		activateEmail(current_user.id)
		response.html('.notificationBar p', 'We\'ve send you another email! Please check your spam folder if you don\'t see it.')
		response.css('*', 'cursor', '')


def hideNotificationBar(response):
	session['hideNotificationBar'] = True
