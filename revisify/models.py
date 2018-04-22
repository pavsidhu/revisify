# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask.ext.login import UserMixin, current_user
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from slugify import UniqueSlugify, slugify
from datetime import datetime, timedelta
from flask import session, url_for
import random

from revisify import db, bcrypt, loginManager, oauth
import utils

def randomLocation():
	locations = [('AF', 'Afghanistan'),
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
		('BO', 'Bolivia, Plurinational State of'),
		('BQ', 'Bonaire, Sint Eustatius and Saba'),
		('BA', 'Bosnia and Herzegovina'),
		('BW', 'Botswana'),
		('BV', 'Bouvet Island'),
		('BR', 'Brazil'),
		('IO', 'British Indian Ocean Territory'),
		('BN', 'Brunei Darussalam'),
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
		('CG', 'Congo'),
		('CD', 'Congo, the Democratic Republic of the'),
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
		('FK', 'Falkland Islands (Malvinas)'),
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
		('HM', 'Heard Island and McDonald Islands'),
		('VA', 'Holy See (Vatican City State)'),
		('HN', 'Honduras'),
		('HK', 'Hong Kong'),
		('HU', 'Hungary'),
		('IS', 'Iceland'),
		('IN', 'India'),
		('ID', 'Indonesia'),
		('IR', 'Iran, Islamic Republic of'),
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
		('KP', 'Korea, Democratic People\'s Republic of'),
		('KR', 'Korea, Republic of'),
		('KW', 'Kuwait'),
		('KG', 'Kyrgyzstan'),
		('LA', 'Lao People\'s Democratic Republic'),
		('LV', 'Latvia'),
		('LB', 'Lebanon'),
		('LS', 'Lesotho'),
		('LR', 'Liberia'),
		('LY', 'Libya'),
		('LI', 'Liechtenstein'),
		('LT', 'Lithuania'),
		('LU', 'Luxembourg'),
		('MO', 'Macao'),
		('MK', 'Macedonia, the former Yugoslav Republic of'),
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
		('FM', 'Micronesia, Federated States of'),
		('MD', 'Moldova, Republic of'),
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
		('MF', 'Saint Martin (French part)'),
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
		('SX', 'Sint Maarten (Dutch part)'),
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
		('TW', 'Taiwan, Province of China'),
		('TJ', 'Tajikistan'),
		('TZ', 'Tanzania, United Republic of'),
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
		('VE', 'Venezuela, Bolivarian Republic of'),
		('VN', 'Vietnam'),
		('VG', 'Virgin Islands, British'),
		('VI', 'Virgin Islands, U.S.'),
		('WF', 'Wallis and Futuna'),
		('EH', 'Western Sahara'),
		('YE', 'Yemen'),
		('ZM', 'Zambia'),
		('ZW', 'Zimbabwe')]
	return random.choice(locations)[0]

def randomSchool():
	schools = ['Adamsdown Primary School',
		'Albany Primary School',
		'All Saints CW Primary School',
		'Allensbank Primary School',
		'Baden Powell Primary School',
		'Birchgrove Primary School',
		'Bishop Childs CW Primary School',
		'Bryn Celyn Primary School',
		'Bryn Deri Primary School',
		'Bryn Hafod Primary School',
		'Christ The King RC Primary School',
		'Coed Glas Primary School',
		'Coryton Primary School',
		'Danescourt Primary School',
		'Fairwater Primary School',
		'Gabalfa Primary School',
		'Gladstone Primary School',
		'Glan-Yr-Afon Primary School',
		'Glyncoed Primary School',
		'Grangetown Primary School',
		'Greenway Primary School',
		'Hawthorn Primary School',
		'Herbert Thompson Primary School',
		'Holy Family RC Primary School',
		'Hywel Dda Primary School',
		'Kitchener Primary School',
		'Lakeside Primary School',
		'Llandaff CW Primary School',
		'Llanedeyrn Primary School',
		'Llanishen Fach Primary School',
		'Llysfaen Primary School',
		'Marlborough Primary School',
		'Meadowlane Primary School',
		'Millbank Primary School',
		'Moorland Primary School',
		'Mount Stuart Primary School',
		'Ninian Park Primary School',
		'Oakfield Primary School',
		'Pen-Y-Bryn Primary School',
		'Pencaerau Primary School',
		'Pentrebane Primary School',
		'Pentyrch Primary School',
		'Peter Lea Primary School',
		'Radnor Primary School',
		'Radyr Primary School',
		'Rhiwbeina Primary School',
		'Rhydypenau Primary School',
		'Roath Park Primary School',
		'Rumney Primary School',
		'Severn Primary School',
		'Springwood Primary School',
		'St Albans RC Primary School',
		'St Bernadettes RC Primary School',
		'St Cadocs RC Primary School',
		'St Cuthberts RC Primary School',
		'St Davids CW Primary School',
		'St Fagans CW Primary School',
		'St Francis RC Primary School',
		'St John Lloyd RC Primary School',
		'St Josephs RC Primary School',
		'St Mary The Virgin CW Primary School',
		'St Marys RC Primary School',
		'St Mellons CW Primary School',
		'St Monicas CW Primary School',
		'St Patricks RC Primary School',
		'St Pauls CW Primary School',
		'St Peters RC Primary School',
		'St Philip Evans RC Primary School',
		'Stacey Primary School',
		'Thornhill Primary School',
		'Ton-Yr-Ywen Primary School',
		'Tongwynlais Primary School',
		'Tredegarville C.W Primary School',
		'Trelai Primary School',
		'Whitchurch Primary School',
		'Willowbrook Primary School',
		'Windsor Clive Primary School']
	return random.choice(schools)


@loginManager.user_loader
def loadUser(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	hash = db.Column(db.String(6))
	name = db.Column(db.String(100), nullable=False, index=True)
	email = db.Column(db.String(320), nullable=False)
	password = db.Column(db.String(60))
	location = db.Column(db.String(2))
	education = db.Column(db.String(255))
	profile = db.Column(db.Boolean, nullable=False, default=True)
	picture = db.Column(db.String(32))
	activated = db.Column(db.Boolean, nullable=False, default=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)
	joined = db.Column(db.DateTime, nullable=False)
	weeklyGoal = db.Column(db.Integer, nullable=False, default=8)

	def __init__(self, name, email, password):
		self.name = name
		self.email = email
		self.password = password
		self.joined = datetime.utcnow()

 	def setPassword(self, password):
 		self.password = bcrypt.generate_password_hash(password)

 	def verifyPassword(self, password):
		# If there is no password set - this happens when users create accounts
		# using their social logins
		if self.password == None:
			return False

 		return bcrypt.check_password_hash(self.password, password)

	@property
	def profilePicture(self):
		if self.picture:
			return {'80': 'https://data.revisify.com/{}/{}_80x80.jpeg'.format(str(self.id), str(self.picture)),
					'270': 'https://data.revisify.com/{}/{}_270x270.jpeg'.format(str(self.id), str(self.picture)),
					'cover': 'https://data.revisify.com/{}/{}_cover.jpeg'.format(str(self.id), str(self.picture)),
					'default': False
					}
		else:
			# Return default user icon
			return {'80': url_for('static', filename='images/userIcon_80x80.png'),
					'270': url_for('static', filename='images/userIcon_270x270.png'),
					'cover': url_for('static', filename='images/userIcon_cover.png'),
					'default': True
					}

	@property
	def shareLink(self):
		string = 'u' + self.hash
		return url_for('social.share', string=string, _external=True)

	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'email': self.email,
			'location': self.location,
			'education': self.education,
			'profile': self.profile,
			'picture': self.picture,
			'activated': self.activated,
			'admin': self.admin,
			'joined': str(self.joined),
			'weeklyGoal': self.weeklyGoal
		}

	@staticmethod
	def generate(count):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py as fake
		from hashids import Hashids

		hashid = Hashids(salt=app.config['SECRET_KEY'], min_length=6)
		seed()
		for i in range(count):
			u = User(name=fake.name.full_name(),
					email=fake.internet.email_address(),
					password=None,
					location=randomLocation(),
					education=randomSchool(),
					profile=True,
					activated=True,
					admin=False)
			db.session.add(u)
			db.session.flush()
			u.hash = hashid.encode(u.id)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()


class OAuth(db.Model):

	__tablename__ = 'oauth'

	id = db.Column(db.Integer, primary_key=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
	socialID = db.Column(db.String(64), nullable=False)
	provider = db.Column(db.String(1), nullable=False)
	accessToken = db.Column(db.Text, nullable=False)
	name = db.Column(db.Text, nullable=False)

	def __init__(self, userID, socialID, provider, accessToken, name):
		self.userID = userID
		self.socialID = socialID
		self.provider = provider
		self.accessToken = accessToken
		self.name = name

	@hybrid_property
	def url(self):
		if self.provider == 'G':
			return 'https://plus.google.com/' + str(self.socialID)
		elif self.provider == 'F':
			return 'https://facebook.com/' + str(self.socialID)

	def serialize(self):
		return {
			'id': self.id,
			'userID': self.userID,
			'socialID': self.socialID,
			'provider': self.provider,
			'accessToken': self.accessToken,
			'name': self.name
		}


class Follow(db.Model):

	__tablename__ = 'follow'

	id = db.Column(db.Integer, primary_key=True)
	follower = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	following = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))

	def __init__(self, follower, following):
		self.follower = follower
		self.following = following

	def serialize(self):
		return {
			'id': self.id,
			'follower': self.follower,
			'following': self.following,
		}


class Subject(db.Model):

	__tablename__ = 'subjects'

	id = db.Column(db.Integer, primary_key=True)
	hash = db.Column(db.String(6))
	accountID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))
	name = db.Column(db.String(100), nullable=False, index=True)
	slug = db.Column(db.String(200), nullable=False)
	color = db.Column(db.Integer, nullable=False)
	date = db.Column(db.DateTime, nullable=False)
	topic = db.relationship('Topic', backref=backref('subject'))
	user = db.relationship('User')

	def __init__(self, accountID, name, color):
		self.accountID = accountID
		self.name = name
		self.color = color
		self.slug = utils.subjectSlug(name)
		self.date = datetime.utcnow()

	@property
	def shareLink(self):
		string = 's' + self.hash
		return url_for('social.share', string=string, _external=True)

	@property
	def colors(self):
		return utils.getColorByNumber(self.color)

	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'userID': self.accountID,
			'color': self.color,
			'date': str(self.date),
		}


class Topic(db.Model):

	__tablename__ = 'topics'

	id = db.Column(db.Integer, primary_key=True)
	hash = db.Column(db.String(6))
	subjectID = db.Column(db.Integer, db.ForeignKey('subjects.id', onupdate='CASCADE', ondelete='CASCADE'))
	name = db.Column(db.String(150), nullable=False, index=True)
	slug = db.Column(db.String(200), nullable=False)
	questions = db.relationship('Question', backref=backref('topic'))
	date = db.Column(db.DateTime, nullable=False)

	def __init__(self, subjectID, name):
		self.subjectID = session['newTopicSubjectID'] = subjectID
		self.name = name
		self.slug = utils.topicSlug(name)
		self.date = datetime.utcnow()

	@property
	def shareLink(self):
		string = 't' + self.hash
		return url_for('social.share', string=string, _external=True)

	@property
	def colors(self):
		return self.subject.colors

	@property
	def user(self):
		return self.subject.user

	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'date': str(self.date),
			'subjectID': self.subjectID,
		}


class Question(db.Model):

	__tablename__ = 'questions'

	id = db.Column(db.Integer, primary_key=True)
	topicID = db.Column(db.Integer, db.ForeignKey('topics.id', onupdate='CASCADE', ondelete='CASCADE'))
	question = db.Column(db.String(8000), nullable=False)
	answer = db.Column(db.String(8000))

	def __init__(self, topicID, question, answer):
		self.topicID = topicID
		self.question = question
		self.answer = answer

	def serialize(self):
		return {
			'id': self.id,
			'title': self.question,
			'answer': self.answer if self.answer != "" else None
		}


class Result(db.Model):

	__tablename__ = 'results'

	id = db.Column(db.Integer, primary_key=True)
	topicID = db.Column(db.Integer, db.ForeignKey('topics.id', onupdate='CASCADE', ondelete='CASCADE'))
	accountID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	date = db.Column(db.DateTime, nullable=False)
	percentage = db.Column(db.String(3), nullable=False)

	def __init__(self, topicID, accountID, percentage):
		self.topicID = topicID
		self.accountID = accountID
		self.date = datetime.utcnow()
		self.percentage = percentage

	def serialize(self):
		return {
			'id': self.id,
			'userID': self.accountID,
			'date': str(self.date),
			'percentage': self.percentage,
		}


class WeeklyGoal(db.Model):

	__tablename__ = 'weekly_goal'

	id = db.Column(db.Integer, primary_key=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	progress = db.Column(db.Integer, nullable=False)
	date = db.Column(db.Date, nullable=False)
	user = db.relationship('User', backref=backref('goal'))

	def __init__(self, progress):
		self.userID = current_user.id
		self.progress = progress
		self.date = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)

	@property
	def total(self):
		return self.user.weeklyGoal

	def completed(self):
		if self.progress >= self.user.weeklyGoal:
			return True
		else:
			return False

	def serialize(self):
		return {
			'id': self.id,
			'userID': self.userID,
			'progress': self.progress,
			'date': str(self.date),
			'user': self.user.serialize(),
		}


class Report(db.Model):

	__tablename__ = 'reports'

	id = db.Column(db.Integer, primary_key=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	issue = db.Column(db.Text(100), nullable=False)
	userReportedID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	date = db.Column(db.DateTime, nullable=False)
	user = db.relationship('User', foreign_keys=[userID])
	userReported = db.relationship('User', foreign_keys=[userReportedID])

	def __init__(self, userID, userReportedID, issue):
		self.userID = userID
		self.userReportedID = userReportedID
		self.issue = issue
		self.date = datetime.utcnow()


class Warning(db.Model):

	__tablename__ = 'warnings'

	id = db.Column(db.Integer, primary_key=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
	issue = db.Column(db.Text(100), nullable=False)
	date = db.Column(db.DateTime, nullable=False)

	def __init__(self, userID, issue):
		self.userID = userID
		self.issue = issue
		self.date = datetime.utcnow()


class Ban(db.Model):

	__tablename__ = 'banned'

	id = db.Column(db.Integer, primary_key=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))
	date = db.Column(db.DateTime, nullable=False)
	user = db.relationship('User', backref=backref('banned'))

	def __init__(self, userID):
		self.userID = userID
		self.date = datetime.utcnow()


class Stats(db.Model):

	__tablename__ = 'stats'

	id = db.Column(db.Integer, primary_key=True)
	users = db.Column(db.Integer, nullable=False)
	subjects = db.Column(db.Integer, nullable=False)
	topics = db.Column(db.Integer, nullable=False)
	questions = db.Column(db.Integer, nullable=False)
	results = db.Column(db.Integer, nullable=False)
	date = db.Column(db.Date, nullable=False)

	def __init__(self, users, subjects, topics, questions, results, date):
		self.users = users
		self.subjects = subjects
		self.topics = topics
		self.questions = questions
		self.results = results
		self.date = datetime.utcnow()


class Help(db.Model):

	__tablename__ = 'help'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	section = db.Column(db.String(100), nullable=False)
	slug = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)

	def __init__(self, title, slug, section, content):
		self.title = title
		self.slug = slug
		self.section = section
		self.content = content
