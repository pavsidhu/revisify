# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, redirect, session
from flask.ext.login import login_required
from revisify.utils import *
from revisify.models import *
from revisify.forms import *

help = Blueprint('help', __name__)

@help.route('/help')
def support():
	basics = db.session.query(Help).filter_by(section='The Basics').all()
	subjectsAndTopics = db.session.query(Help).filter_by(section='Subjects and Topics').all()
	studying = db.session.query(Help).filter_by(section='Studying').all()
	gamification = db.session.query(Help).filter_by(section='Gamification').all()
	yourAccount = db.session.query(Help).filter_by(section='Your Account').all()
	socialHelp = db.session.query(Help).filter_by(section='Social').all()
	other = db.session.query(Help).filter_by(section='Other').all()

	return render_template('help/help.html',
							basics = basics,
							subjectsAndTopics = subjectsAndTopics,
							studying = studying,
							gamification = gamification,
							yourAccount = yourAccount,
							# This is named socialHelp since there is a Jinja
							# macro named 'social'
							socialHelp = socialHelp,
							other = other)


@help.route('/help/<slug>')
def article(slug):
	article = db.session.query(Help).filter_by(slug=slug).one()
	return render_template('help/article.html', article=article)
