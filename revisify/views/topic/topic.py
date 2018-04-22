# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, url_for, flash, request
from flask.ext.login import login_required, current_user
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
from slugify import UniqueSlugify
from datetime import datetime
import re

topic = Blueprint('topic', __name__)

@topic.route('/<hash>/<subjectSlug>/<topicSlug>/overview', methods=['POST', 'GET'])
def overview(hash, subjectSlug, topicSlug):
	topic = topicFromHash(hash)

	# If the subject and topic slugs for the given hash are incorrect, then
	# redirect the user to the link with the correct slugs.
	if topic.subject.slug != subjectSlug or topic.slug != topicSlug:
		return redirect(url_for('topic.overview', hash=hash, subjectSlug=topic.subject.slug, topicSlug=topic.slug))

	# Get list of topics for validation to prevent duplicate names
	topics = [t for t in getTopics(topic.subject.id) if t['name'] != topic.name]

	if current_user.is_anonymous() or current_user.id != topic.subject.accountID:
		ownTopic = False
		user = getUser(topic.subject.accountID)

		# Show not found page if the user is set to private
		if not user.profile:
			abort(404)
	else:
		ownTopic = True
		user = current_user

	if current_user.is_anonymous():
		resultsDate = None
		resultsPercentage = None
	else:
		resultsDate = list(reversed(db.session.query(Result).filter_by(accountID=current_user.id, topicID=topic.id).order_by(Result.id.desc()).limit(7).all()))
		resultsPercentage = list(reversed(db.session.query(Result).filter_by(accountID=current_user.id, topicID=topic.id).order_by(Result.id.desc()).limit(7).all()))

		for result in resultsDate:
			result.date = str(result.date)[5:7] + '/' + str(result.date)[8:10]

	# Get last result, will return error if no last result is available
	try:
		lastResult = int(resultsPercentage[-2].percentage)
	except:
		lastResult = None

	if request.method == 'POST':
		error = False

		# Get form contents
		topicName = request.form['topicName']

		# Error validation is also server side in case someone maliciously
		# manipulates the client side Javascript validation
		if topicName.strip(' \t\n\r') == '':
			error = True
		if not bool(re.compile(r'.*[A-Za-z0-9].*').search(topicName)):
			error = True
		if topicName.lower() in (t['name'].lower() for t in topics):
			error = True

		questions = []
		i = 1

		while True:
			# Receive question from form if it exists, if not then end the loop
			try:
				question = request.form['question' + str(i)]
				answer = request.form['answer' + str(i)]
			except:
				break

			# Stop loop if question is empty
			if question == '':
				error = True
				break

			# Add question to list
			questions.append({
				'question': question,
				'answer': answer,
			})

			i += 1

		# Confirm there are more than 2 and less than 100 questions
		if i < 2 or i > 100:
			error = True

		if not error:
			# Update topic name and slug if changed
			if topic.name != topicName:
				topic.name = topicName

				# Update slug of topic
				session['newTopicSubjectID'] = topic.subject.id
				topicSlug = UniqueSlugify(unique_check=uniqueTopicSlug, to_lower=True)
				topic.slug = topicSlug(topic.name)

			# Update last updated date of subject and topic
			topic.date = datetime.utcnow()
			topic.subject.date = datetime.utcnow()

			# Delete all the old questions of that topic
			db.session.query(Question).filter_by(topicID=topic.id).delete()

			# Add questions to database
			for q in questions:
				row = Question(topicID=topic.id, question=q['question'], answer=q['answer'])
				db.session.add(row)

			db.session.commit()

	# Get colors
	color = getColor(topic.subject.id)
	textcolor = color['text']
	iconcolor = color['icon']
	bgcolor = color['bg']
	navcolor = color['nav']

	# Get topic questions
	userQuestions = db.session.query(Question).filter_by(topicID=topic.id).join(Topic).join(Subject).filter(Subject.accountID==user.id).order_by(Question.id)
	questions = []
	count = 1
	for question in userQuestions:
		questions.append(dict(number=count, question=question.question, answer=question.answer))
		count += 1

	return render_template('topic/overview.html',
							topic = topic,
							ownTopic = ownTopic,
							user = user,
							questions = questions,
							topics = topics,
							resultsDate = resultsDate,
							resultsPercentage = resultsPercentage,
							textcolor = textcolor,
							iconcolor = iconcolor,
							bgcolor = bgcolor,
							navcolor = navcolor)


@topic.route('/<hash>/<slug>/topic/new', methods=['POST', 'GET'])
@login_required
def new(hash, slug):
	subject = subjectFromHash(hash)

	if subject.slug != slug:
		return redirect(url_for('topic.new', hash=hash, slug=subject.slug))

	session['subject'] = subject.name # This is used to prevent duplicate subjects in form validation
	topics = getTopics(subject.id)

	if request.method == 'POST':
		error = False

		# Get form contents
		topicName = request.form['topicName']

		# Error validation is also server side in case someone maliciously
		# manipulates the client side Javascript validation
		if topicName.strip(' \t\n\r') == '':
			error = True
		if not bool(re.compile(r'.*[A-Za-z0-9].*').search(topicName)):
			error = True
		if topicName.lower() in (t['name'].lower() for t in topics):
			error = True

		questions = []
		i = 1

		while True:
			# Receive question from form if it exists, if not then end the loop
			try:
				question = request.form['question' + str(i)]
				answer = request.form['answer' + str(i)]
			except:
				break

			# Stop loop if question is empty
			if question == '':
				error = True
				break

			# Add question to list
			questions.append({
				'question': question,
				'answer': answer,
			})

			i += 1

		# Confirm there are more than 2 and less than 100 questions
		if i < 2 or i > 100:
			error = True

		# Create topic once validation is passed
		if not error:
			newTopic = Topic(subjectID=subject.id, name=topicName)
			db.session.add(newTopic)

			db.session.flush()
			newTopic.hash = hashID(newTopic.id)
			newTopic.subject.date = datetime.now() # Check if this is needed

			db.session.commit()

			# Add questions to database
			for q in questions:
				row = Question(topicID=newTopic.id, question=q['question'], answer=q['answer'])
				db.session.add(row)

			db.session.commit()
			return redirect(url_for('topic.overview', hash=newTopic.hash, subjectSlug=newTopic.subject.slug, topicSlug=newTopic.slug))

	# Get colors
	color = getColor(subject.id)
	textcolor = color['text']
	iconcolor = color['icon']
	bgcolor = color['bg']
	navcolor = color['nav']

	return render_template('topic/new.html', topics=topics, textcolor=textcolor, iconcolor=iconcolor, bgcolor=bgcolor, navcolor=navcolor)


@topic.route('/deleteTopic/', methods=['POST', 'GET'])
@login_required
def delete():
	id = request.form['topicToDelete']

	topic = getTopicByID(id)
	subject = topic.subject

	if current_user.admin or topic.subject.accountID == current_user.id:
		db.session.query(Topic).filter_by(id=id).delete(synchronize_session='fetch')

	db.session.commit()
	return redirect(url_for('subject.subjectList',
							hash = subject.hash,
							slug = subject.slug
							)
					)
