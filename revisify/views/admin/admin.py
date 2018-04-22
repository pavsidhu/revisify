# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import Blueprint, render_template, url_for, redirect, g, send_file
from revisify.utils import *
from revisify.models import *
from werkzeug.security import gen_salt
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from random import randint
import textwrap, flask_sijax, cStringIO, base64, requests

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('', methods=['POST', 'GET'])
@admin_required
def panel():
	def createSocialImage(response, form):
		title = form['title']
		text = form['text']
		color = getColorByNumber(randint(0,9))

		# Convert hex values of color to RGB
		for key, value in color.items():
			if key != 'id':
				value = value.lstrip('#')
				value = hexToRGB(value)

		#  Create image
		image = Image.new('RGB', (1080, 1080), color=color['bg'])

		# Adds fold in top right corner
		draw = ImageDraw.Draw(image)
		draw.polygon([(1080, 0), (1080, 180), (900, 0),], fill = color['text'])
		draw.polygon([(900, 180), (1080, 180), (900, 0),], fill = color['nav'])

		# Add logo in bottom right
		logo = Image.open('revisify/static/images/socialImage/{}.png'.format(color['id']))
		image.paste(logo, (0,0), mask=logo)

		# Add title to image
		font = ImageFont.truetype('revisify/static/fonts/texta-regular-webfont.ttf', 150)
		w, h = draw.textsize(title, font)
		draw.text((540 - (w/2), 350), title, color['text'], font=font)

		# Add description text to image
		font = ImageFont.truetype('revisify/static/fonts/texta-regular-webfont.ttf', 60)

		wrap = textwrap.wrap(text, width=35)
		for i, line in enumerate(wrap):
				w, h = draw.textsize(line, font)
				draw.text((540 - (w/2), 550 + (70*i)), line, color['text'], font=font)

		imageBuffer = cStringIO.StringIO()
		image.save(imageBuffer, 'PNG', quality=100)

		imageString = base64.b64encode(imageBuffer.getvalue())
		imageString = 'data:image/png;base64,{}'.format(imageString)

		response.call('showSocialImage', [imageString])

	if g.sijax.is_sijax_request:
		g.sijax.register_callback('createSocialImage', createSocialImage)

		g.sijax.register_callback('confirmEmail', confirmEmail)
		g.sijax.register_callback('hideNotificationBar', hideNotificationBar)

		return g.sijax.process_request()

	# Current total stats
	users = db.session.query(User).count()
	subjects = db.session.query(Subject).count()
	topics = db.session.query(Topic).count()
	questions = db.session.query(Question).count()
	results = db.session.query(Result).count()
	reports = db.session.query(Report).count()

	# Stats for graph
	dateList = reversed(db.session.query(Stats.date).order_by(Stats.id.desc()).limit(60).all()[::3])
	usersList = reversed(db.session.query(Stats.users).order_by(Stats.id.desc()).limit(60).all()[::3])
	subjectsList = reversed(db.session.query(Stats.subjects).order_by(Stats.id.desc()).limit(60).all()[::3])
	topicsList = reversed(db.session.query(Stats.topics).order_by(Stats.id.desc()).limit(60).all()[::3])
	questionsList = reversed(db.session.query(Stats.questions).order_by(Stats.id.desc()).limit(60).all()[::3])
	resultsList = reversed(db.session.query(Stats.results).order_by(Stats.id.desc()).limit(60).all()[::3])

	return render_template('admin/admin.html', users=users, subjects=subjects, topics=topics, questions=questions, results=results, reports=reports, dateList=dateList, usersList=usersList, subjectsList=subjectsList, topicsList=topicsList, questionsList=questionsList, resultsList=resultsList)

@admin.route('/reports')
@admin_required
def reports():
	reportTotal = db.session.query(Report).count()
	reportedUsers = db.session.query(Report).distinct(Report.userReportedID).group_by(Report.userReportedID)
	reportedUsersTotal = db.session.query(Report).distinct(Report.userReportedID).group_by(Report.userReportedID).count()
	reports = db.session.query(Report)
	userStatus = {}
	for user in reportedUsers:
		userStatus[user.userReportedID] = str(db.session.query(Warning).filter_by(userID=user.userReportedID).count())

	return render_template('admin/reports.html', reportTotal=reportTotal, reports=reports, reportedUsers=reportedUsers, reportedUsersTotal=reportedUsersTotal, userStatus=userStatus)


@admin.route('/new-blog-post', methods=['POST'])
@admin_required
def newBlogPost():
	title = request.form['title']
	creator = current_user.name
	content = request.form['blogpost']
	date = datetime.today()

	# Add blog to database
	post = Post(title, content, date, creator)
	db.session.add(post)
	db.session.commit()
	return redirect(url_for('blog.blogPage'))


@admin.route('/add-admin', methods=['GET', 'POST'])
@admin_required
def add():
	email = request.form['email'].lower()
	user = db.session.query(User).filter_by(email=email).one()
	user.admin = True
	db.session.commit()

	login = user.name.replace(" ", "").lower()

	# Create an email address for the admin
	requests.post(
		"https://api.mailgun.net/v3/domains/revisify.com/credentials",
		auth=("api", "key-b323c4be7e76015ad633646d7e81c420"),
		data={"login": login,
				"password": "giraffe"})

	return redirect(url_for('admin.panel'))


@admin.route('/remove-admin/', methods=['GET', 'POST'])
@admin_required
def remove():
	email = request.form['email'].lower()
	user = db.session.query(User).filter_by(email=email).one()
	user.admin = False
	db.session.commit()

	# Removes admin email address
	login = user.name.replace(" ", "").lower()
	requests.delete(
		"https://api.mailgun.net/v3/domains/revisify.com/credentials/{}".format(login),
		auth=("api", "key-b323c4be7e76015ad633646d7e81c420")
		)

	return redirect(url_for('admin.panel'))


@admin.route('/change-email-password/', methods=['GET', 'POST'])
@admin_required
def changeEmailPassword():
	password = request.form['password']
	login = current_user.name.replace(" ", "").lower()

	# change admin email address password
	requests.put(
		"https://api.mailgun.net/v3/domains/revisify.com/credentials/{}".format(login),
		auth=("api", "key-b323c4be7e76015ad633646d7e81c420"),
		params={ password: password }
		)

	return redirect(url_for('admin.panel'))


@admin.route('/delete-report/<reportID>/', methods=['GET', 'POST'])
@admin_required
def deleteReport(reportID):
	# Clears reports from table
	db.session.query(Report).filter_by(id=reportID).delete()
	db.session.commit()

	return redirect(request.referrer)


@admin.route('/delete-warning/<warningID>/', methods=['GET', 'POST'])
@admin_required
def deleteWarning(warningID):
	# Clears reports from table
	db.session.query(Warning).filter_by(id=warningID).delete()
	db.session.commit()

	return redirect(request.referrer)


@admin.route('/remove-picture/<userID>', methods=['GET', 'POST'])
@admin_required
def removePicture(userID):
	# Remove user profile picture
	user = db.session.query(User).filter_by(id=userID).one()
	user.picture = None
	db.session.commit()

	return redirect(request.referrer)

# @admin.route('/sendEmail', methods=['GET', 'POST'])
# @admin_required
# def sendEmail():
# 	users = db.session.query(User).all()
# 	for user in users:
# 		name = user.name
# 		print name
# 		email = user.email.lower()
# 		html = render_template('1.1.html', name=name)
# 		requests.post(
# 			"https://api.mailgun.net/v3/revisify.com/messages",
# 			auth=("api", "key-b323c4be7e76015ad633646d7e81c420"),
# 			data={"from": app.config['MAIL_DEFAULT_SENDER'],
# 				  "to": [name + " <" + email + ">"],
# 				  "subject": "Introducing New Features to Revisify",
# 				  "html": html,
# 				  "text": "Hi " + name + ",\r\n\r\nWe're excited to announce that we have released some exciting new features on Revisify to improve your workflow.\r\n\r\nAll New Topic Editor\r\n\r\nWe remade the topic editor with simplicity and functionality in mind. Previously only answers could be formatted however images, links and more can now be added to your question too. We also have one toolbar (rather then one per question as before) with new bold and italic text options.\r\n\r\nImages, links, lists and more can now be seen as you write your questions to make creating topics that much easier. As well as this, questions can be added in the middle of a topic which has been requested by many students.\r\n\r\nIf you would like more detail on the new topic editor, read our Creating a Topic section in our new Help Center.\r\n\r\nHelp Center\r\n\r\nAll the information needed to using Revisify can be found at our new Help Center. From testing yourself to changing your profile picture, we have details on everything you need to know.\r\n\r\nAnd More Features\r\n\r\nThe search bar will now show subjects and topics from all students, not just those you follow. We have added the option to update the name to your account too.\r\n\r\nLastly...\r\n\r\nWe love to hear feedback from you! Please let us know your thoughts on our latest update. If you come across any issues, please let us know.\r\n\r\nThanks,\r\nThe Revisify Team.\r\n\r\nReceived this email by mistake? We're sorry, just ignore it."
# 				  })
# 	return 'success'
