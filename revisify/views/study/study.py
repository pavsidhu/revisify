# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, g
from flask.ext.login import login_required, current_user

from datetime import datetime, timedelta
import flask_sijax

from revisify.utils import *
from revisify.forms import *
from revisify.models import *

study = Blueprint('study', __name__)

@study.route('/<string:hash>/<subjectSlug>/<topicSlug>/test', methods=['POST', 'GET'])
def test(hash, subjectSlug, topicSlug):
	topic = topicFromHash(hash)

	# Redirect to link with correct slugs. Slugs are checked to see if they are
	# correct based on the hash provided in the URL
	if topic.subject.slug != subjectSlug or topic.slug != topicSlug:
		return redirect(url_for('study.test', hash=hash, subjectSlug=topic.subject.slug, topicSlug=topic.slug))

	# Show not found page if the user is set to private
	if not topic.user.profile:
		if current_user.is_anonymous():
			abort(404)
		elif topic.user.id != current_user.id:
			abort(404)

	# Get colors - these values are used in default.html
	textcolor = topic.colors['text']
	iconcolor = topic.colors['icon']
	bgcolor = topic.colors['bg']
	navcolor = topic.colors['nav']

	def result(response, score):
		percentage = int(float(score) / float(len(topic.questions)) * 100)

		if current_user.is_anonymous():
			response.call('resultsPage', [percentage])
		else:
			# Log the result of the test
			result = Result(topic.id, current_user.id, percentage)
			db.session.add(result)

			# Update weekly goal if the test result is 90% or higher
			weeklyGoal = db.session.query(WeeklyGoal).filter_by(userID=current_user.id, date=getSundayDate())

			if weeklyGoal.count() == 1:
				# If this weeks goal has already started
				weeklyGoal = weeklyGoal.one()
			elif percentage >= 90:
				# Create a record for this weeks goal if this test is greater
				# than 90%
				weeklyGoal = WeeklyGoal(progress=0)
				db.session.add(weeklyGoal)
			else:
				# Create a weekly goal object so that it can send the data to
				# the client, however it is not sent to the database since we
				# since it is not needed
				weeklyGoal = WeeklyGoal(progress=0)
				weeklyGoal.user = current_user

			if percentage >= 90:
				weeklyGoal.progress += 1

				# Set this week's goal as completed
				if weeklyGoal.progress == current_user.weeklyGoal:
					weeklyGoal.completed = True

			db.session.commit()

			# Get previous results on topic - two queries as Jinja cannot have 2 for loops of same list for some reason
			resultsQuery = list(reversed(db.session.query(Result).filter_by(accountID=current_user.id, topicID=topic.id).order_by(Result.id.desc()).limit(7).all()))
			results = []

			for result in resultsQuery:
				results.append({
					'percentage': result.percentage,
					'date': str(result.date)[5:7] + '/' + str(result.date)[8:10]
				})

			response.call('resultsPage', [percentage, results, weeklyGoal.serialize()])

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('result', result)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)

		return g.sijax.process_request()

	return render_template('study/test.html',
							topic = topic,
							mode = 'test',
							textcolor = textcolor,
							iconcolor = iconcolor,
							bgcolor = bgcolor,
							navcolor = navcolor)

@study.route('/<string:hash>/<subjectSlug>/<topicSlug>/practice', methods=['POST', 'GET'])
def practice(hash, subjectSlug, topicSlug):
	topic = topicFromHash(hash)

	# Redirect to link with correct slugs. Slugs are checked to see if they are
	# correct based on the hash provided in the URL
	if topic.subject.slug != subjectSlug or topic.slug != topicSlug:
		return redirect(url_for('study.test', hash=hash, subjectSlug=topic.subject.slug, topicSlug=topic.slug))

	# Show not found page if the user is set to private
	if not topic.user.profile:
		if current_user.is_anonymous():
			abort(404)
		elif topic.user.id != current_user.id:
			abort(404)

	# Get colors - these values are used in default.html
	textcolor = topic.colors['text']
	iconcolor = topic.colors['icon']
	bgcolor = topic.colors['bg']
	navcolor = topic.colors['nav']

	return render_template('study/practice.html',
							topic = topic,
							mode = 'practice',
							textcolor = textcolor,
							iconcolor = iconcolor,
							bgcolor = bgcolor,
							navcolor = navcolor)
