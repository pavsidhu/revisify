# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session, request, abort
from flask.ext.login import login_required, current_user
from revisify.utils import *
from revisify.models import *
from revisify.forms import *
from datetime import datetime

subject = Blueprint('subject', __name__)

@subject.route('/<string:hash>/<slug>/topics', methods=['POST', 'GET'])
def subjectList(slug, hash):
	subject = subjectFromHash(hash)

	if subject.slug != slug:
		return redirect(url_for('subject.subjectList', hash=hash, slug=subject.slug))

	topics = getTopics(subject.id)

	# Get colors
	color = getColor(subject.id)
	textcolor = color['text']
	iconcolor = color['icon']
	bgcolor = color['bg']
	navcolor = color['nav']

	if current_user.is_anonymous() or current_user.id != subject.accountID:
		ownSubject = False

		# Show not found page if the user is set to private
		if not subject.user.profile:
			abort(404)
	else:
		ownSubject = True

	# Receive following users
	return render_template('subject/subject.html',
							subject = subject,
							topics = topics,
							ownSubject = ownSubject,
							textcolor = textcolor,
							iconcolor = iconcolor,
							bgcolor = bgcolor,
							navcolor = navcolor)


@subject.route('/new-subject', methods=['POST', 'GET'])
@login_required
def new():
	form = newSubjectForm()

	if form.validate_on_submit():
		name = form.name.data
		color = form.color.data
		subject = Subject(current_user.id, name, color)
		db.session.add(subject)
		db.session.flush()
		subject.hash = hashID(subject.id)
		db.session.commit()
		return redirect('/')

	return render_template('subject/newSubject.html', form=form)


@subject.route('/<hash>/<slug>/edit', methods=['POST', 'GET'])
@login_required
def edit(hash, slug):
	subject = subjectFromHash(hash)

	if subject.slug != slug:
		return redirect(url_for('subject.edit', hash=hash, slug=subject.slug))

	color = getColor(subject.id)['id']
	edit = True

	form = editSubjectForm()

	if form.validate_on_submit():

		# If the subject name is the same, then do not change it
		# This prevents the slug from changing i.e. /physics to /physics-1
		if subject.name != form.name.data:
			subject.name = form.name.data
			subject.slug = subjectSlug(form.name.data)

		subject.color = form.color.data

		db.session.commit()

		return redirect(url_for('subject.subjectList', hash=subject.hash, slug=subject.slug))

	return render_template('subject/newSubject.html', form=form, edit=edit, subject=subject, color=color)


@subject.route('/delete/', methods=['POST', 'GET'])
@login_required
def delete():
	id = request.form['subjectToDelete']
	subject = db.session.query(Subject).filter_by(id=id).one()
	userID = subject.accountID
	if current_user.admin and userID != current_user.id:
		db.session.query(Subject).filter_by(id=id).delete()
		db.session.commit()
		user = getUser(userID)
		return redirect(url_for('social.user', hash=user.hash))
	else:
		db.session.query(Subject).filter_by(accountID=current_user.id, id=id).delete()
		db.session.commit()
		return redirect('/')
