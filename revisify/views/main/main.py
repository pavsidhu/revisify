# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, url_for, g
from flask.ext.login import current_user, login_required
from sqlalchemy import or_
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
import requests, math, flask_sijax

main = Blueprint('main', __name__)

@main.route('/', methods=['POST', 'GET'])
def index():
	if current_user.is_anonymous():

		# Used to add styles to the navigation bar in default.html
		welcome = True

		return render_template('main/welcome.html', welcome=welcome)

	# Receive subjects in order of last active
	query = db.session.query(Subject).filter_by(accountID=current_user.id).order_by(Subject.date.desc())

	subjectList = []
	for subject in query:
		color = getColorByNumber(subject.color)
		percentage = getSubjectPercentage(subject.id)

		contentLink = url_for('subject.subjectList', hash=subject.hash, slug=subject.slug)

		subjectList.append({
			'id': subject.id,
			'name': subject.name,
			'hash': subject.hash,
			'slug': subject.slug,
			'contentLink': contentLink,
			'percentage': percentage,
			'textcolor': color['text'],
			'iconcolor': color['icon'],
		})

	following = followedUsers(current_user.id)

	weeklyGoal = getWeeklyGoal(current_user.id)
	studyStreakResults = getStudyStreakResults(current_user.id)

	def editWeeklyGoal(response, goal):
		if not goal < 1 or not goal > 40:
			current_user.weeklyGoal = goal
			db.session.commit()

			progress = getWeeklyGoalProgress(current_user.id)

			response.call('hidePopup')

			# Update weekly goal section text
			response.html('.weeklyGoal .weeklyGoalFraction', '{}/{}'.format(progress, goal))

			# Update weekly goal section progress circle
			circumference = 3.14159265359 * (2 * 80)

			percentage = float(progress) / float(goal)
			strokeDashoffset = circumference - (percentage * circumference)

			response.css('.weeklyGoalChart .weeklyGoalChartProgress', 'transition-delay', 500)

			if percentage > 1.0:
				strokeDashoffset = 0.0

			response.css('.weeklyGoalChart .weeklyGoalChartProgress', 'stroke-dashoffset', strokeDashoffset)
			response.css('*', 'cursor', 'auto')

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('editWeeklyGoal', editWeeklyGoal)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)

		return g.sijax.process_request()

	return render_template('main/subjects.html',
							subjectList = subjectList,
							following = following,
							weeklyGoal = weeklyGoal,
							studyStreakResults = studyStreakResults)


@main.route('/search', methods=['POST', 'GET'])
@login_required
def search():
	originalQuery = request.args.get('query')
	query = re.escape(originalQuery)
	query.replace('\\', '')

	# If pressed the search button with no query
	if query == '':
		noResults = True
		return render_template('main/search.html',
								originalQuery = originalQuery,
								noResults = noResults)

	# Create a list of user IDs we want to get results for including the current user and following users
	usersID = []
	for user in followedUsers(current_user.id):
		usersID.append(user['id'])
	usersID.append(current_user.id)

	noResults = noUsers = noSubjects = noTopics = False

	subjectOwnResult = []
	subjectFollowingResult = []
	subjectOtherResult = []

	topicOwnResult = []
	topicFollowingResult = []
	topicOtherResult = []

	userResult = []

	itemsPerPage = 15

	# NOTICE: Regex only works with MySQL databases

	subjectQuery = db.session.query(Subject).filter(Subject.name.op('REGEXP')(u'[[:<:]]{}'.format(query))).order_by(Subject.id.desc())
	def subjectSearch(page):
		lowerBound = (itemsPerPage * (page - 1)) - 1
		upperBound = (itemsPerPage * page) - 1

		if lowerBound == -1:
			lowerBound = 0

		for subject in subjectQuery.all()[lowerBound:upperBound]:
			if subject.accountID != current_user.id: # If the subject is not the users
				if subject.user.profile == True: # Check if user is set to private
					if subject.accountID in usersID:
						# If the subject is that of a following user
						subjectFollowingResult.append({
							'subject': subject.name,
							'hash': subject.hash,
							'slug': subject.slug,
							'user': subject.user,
							'icon': subject.user.profilePicture,
							'textcolor': subject.colors['text'],
							'iconcolor': subject.colors['icon']
						})
					else:
						# If the subject is that of a non following user
						subjectOtherResult.append({
							'subject': subject.name,
							'hash': subject.hash,
							'slug': subject.slug,
							'user': subject.user,
							'icon': subject.user.profilePicture,
							'textcolor': subject.colors['text'],
							'iconcolor': subject.colors['icon']
						})
			else: # If own subject
				subjectOwnResult.append({
					'subject': subject.name,
					'hash': subject.hash,
					'slug': subject.slug,
					'user': subject.user,
					'icon': subject.user.profilePicture,
					'textcolor': subject.colors['text'],
					'iconcolor': subject.colors['icon']
				})

		# Create one big subject list
		subjectResult = subjectOwnResult + subjectFollowingResult + subjectOtherResult

		return subjectResult

	topicQuery = db.session.query(Topic).filter(Topic.name.op('REGEXP')(u'[[:<:]]{}'.format(query))).join(Subject).order_by(Topic.id.desc())
	def topicSearch(page):
		lowerBound = (itemsPerPage * (page - 1)) - 1
		upperBound = (itemsPerPage * page) - 1

		if lowerBound == -1:
			lowerBound = 0

		lowerBound = (page * 15) - 15
		upperBound = (page * 15) - 1

		for topic in topicQuery.all()[lowerBound:upperBound]:
			color = getColor(topic.subject.id)

			if topic.subject.accountID != current_user.id: # If the topic is not the users
				# Check if user is set to private
				if topic.user.profile == True:
					if topic.subject.accountID in usersID: # If the topic is that of a following user
						topicFollowingResult.append({
							'topic': topic.name,
							'hash': topic.hash,
							'slug': topic.slug,
							'user': topic.user,
							'icon': topic.user.profilePicture,
							'subject': topic.subject.name,
							'subjectSlug': topic.subject.slug,
							'textcolor': topic.colors['text'],
							'iconcolor': topic.colors['icon']
						})

					else:
						topicOtherResult.append({
							'topic': topic.name,
							'hash': topic.hash,
							'slug': topic.slug,
							'user': topic.user,
							'icon': topic.user.profilePicture,
							'subject': topic.subject.name,
							'subjectSlug': topic.subject.slug,
							'textcolor': topic.colors['text'],
							'iconcolor': topic.colors['icon']
						})

			else: # If own topic
				topicOwnResult.append({
					'topic': topic.name,
					'hash': topic.hash,
					'slug': topic.slug,
					'user': topic.user,
					'icon': topic.user.profilePicture,
					'subject': topic.subject.name,
					'subjectSlug': topic.subject.slug,
					'textcolor': topic.colors['text'],
					'iconcolor': topic.colors['icon']
				})

		# Create one big topic list
		topicResult = topicOwnResult + topicFollowingResult + topicOtherResult

		return topicResult

	userQuery = db.session.query(User).filter(User.name.op('REGEXP')(u'[[:<:]]{}'.format(query))).order_by(User.id.desc())
	def userSearch(page):
		lowerBound = (itemsPerPage * (page - 1)) - 1
		upperBound = (itemsPerPage * page) - 1

		if lowerBound == -1:
			lowerBound = 0

		for user in userQuery.all()[lowerBound:upperBound]:
			# Check if user already in list - this prevents duplicate users showing
			# in search when searching 'John Smith' and there is a user called 'John Smith'
			# i.e. the two words in the query are matched twice with each word in John Smith's name
			alreadyFound = False
			for userFound in userResult:
				if user.id == userFound['id']:
					alreadyFound = True

			# If they have a public profile and it is not the user's own account
			if user.profile is True and alreadyFound == False:
				userResult.append({
					'id': user.id,
					'hash': user.hash,
					'name': user.name,
					'education': user.education,
					'location': getLocation(user.location),
					'icon': user.profilePicture
				})

		return userResult

	def loadMore(response, page):
		response.call('addPage');

		for subject in subjectSearch(page):
			link = url_for('subject.subjectList',
							hash=subject['hash'],
							slug=subject['slug'])

			response.call('addSearchItem', [
							'subjects',
							subject['subject'],
							subject['user'].name,
							link,
							subject['icon']['80'],
							subject['textcolor'],
							subject['iconcolor']
							])

		for topic in topicSearch(page):
			link = url_for('topic.overview',
							hash=topic['hash'],
							subjectSlug=topic['subjectSlug'],
							topicSlug=topic['slug'])

			response.call('addSearchItem', [
							'topics',
							topic['topic'],
							topic['user'].name,
							link,
							topic['icon']['80'],
							topic['textcolor'],
							topic['iconcolor']
							])

		for user in userSearch(page):
			link = url_for('social.user', hash=user['hash'])

			response.call('addSearchItem', [
							'people',
							user['name'],
							user['education'],
							link,
							user['icon']['80']
							])


	if g.sijax.is_sijax_request:
		g.sijax.register_callback('loadMore', loadMore)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)

		return g.sijax.process_request()

	subjectResult = subjectSearch(1)
	topicResult = topicSearch(1)
	userResult = userSearch(1)

	if subjectResult == [] and topicResult == [] and userResult == []:
		noResults = True

	return render_template(
				'main/search.html',
				originalQuery = originalQuery,
				subjectResult = subjectResult,
				topicResult = topicResult,
				userResult = userResult,
				noResults = noResults
				)
