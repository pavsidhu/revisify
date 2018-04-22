# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask import session
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, PasswordField, RadioField, BooleanField, SelectField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Email, Length, Regexp, ValidationError
from utils import getSubjectNames, checkPassword, checkEmail
from models import *

# Account Forms --------------------------------------------------------------------------------------------------------------

class loginForm(Form):
    email = EmailField('email', validators=[InputRequired("Please enter your email address."), Email("Please enter a valid email address.")])
    password = PasswordField('password', validators=[InputRequired("Please enter your password.")])
    remember = BooleanField('Remember me?')


class registerForm(Form):
    name = StringField('name', validators=[InputRequired("Please enter your full name."), Length(max=100, message="Your name cannot be longer than 50 characters.")])
    email = EmailField('email', validators=[InputRequired("Please enter your email address."), Email("Please enter a valid email address."), Length(max=320, message="Your email cannot be longer than 320 characters.")])
    password = PasswordField('password', validators=[InputRequired("Please enter a password."), Length(min=5, message="Your password must be at least 5 characters.")])
    remember = BooleanField('Remember me?')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).first():
            raise ValidationError('The email you entered is already registered.')

# User Profile Forms ---------------------------------------------------------------------------------------------------------

class profileUserDetailsForm(Form):
    name = StringField('name', validators=[Length(max=100, message="Your name cannot be longer than 100 characters.")])
    location = SelectField('location', choices=[
        ('', 'Choose your country'),
        ('AF', 'Afghanistan'),
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
        ('ZW', 'Zimbabwe')])
    education = StringField('education', validators=[Length(max=100, message="Your place of education cannot be longer than 100 characters.")])

    def validate_location(self, location):
        if location.data == '':
            self.location.data = None


class setupProfilePictureForm(Form):
    crop = StringField('profile picture', validators=[InputRequired('There was an error uploading your profile picture.')])


class setupUserDetailsForm(Form):
    location = SelectField('location', choices=[
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
        ('ZW', 'Zimbabwe')])
    education = StringField('education', validators=[Length(max=100, message="Your place of education cannot be longer than 100 characters.")])

    def validate_location(self, location):
        if location.data == '':
            self.location.data = None

# Subject/Topic Forms --------------------------------------------------------------------------------------------------------

def duplicateSubject(form, field):
    subjectList = getSubjectNames(current_user.id)
    if field.data.lower() in subjectList:
        raise ValidationError('You already have a subject with this name.')


def duplicateTopic(form, field):
    subject = session['subject']
    topicList = getTopicNames(current_user.id, subject)
    if field.data.lower() in topicList:
        raise ValidationError('You already have a topic with this name.')


class newSubjectForm(Form):
    name = StringField('name', validators=[InputRequired("Please enter a subject name."), duplicateSubject, Regexp('.*[A-Za-z0-9].*', message="Subject names must contain at least one letter or number.")])
    color = RadioField('Label', choices=[('0', 'Red'), ('1', 'Pink'), ('2', 'Purple'), ('3', 'Blue'), ('4', 'Cyan'), ('5', 'Teal'), ('6', 'Green'), ('7', 'Lime'), ('8', 'Orange'), ('9', 'Brown')])


class editSubjectForm(Form):
    name = StringField('name', validators=[InputRequired("Please enter a subject name."), Regexp('.*[A-Za-z0-9].*', message="Subject names must contain at least one letter or number.")])
    oldName = StringField()
    color = RadioField('Label', choices=[('0', 'Red'), ('1', 'Pink'), ('2', 'Purple'), ('3', 'Blue'), ('4', 'Cyan'), ('5', 'Teal'), ('6', 'Green'), ('7', 'Lime'), ('8', 'Orange'), ('9', 'Brown')])

    def validate_name(self, field):
        oldName = self.oldName.data.title()
        subjectList = getSubjectNames(current_user.id)
        if field.data.title() in subjectList and field.data.title() != oldName:
            raise ValidationError('You already have a subject with this name.')


class reportForm(Form):
    issue = StringField('issue', validators=[InputRequired("Please enter your issue."), Length(max=255, message="Your report cannot be longer than 255 characters.")])


class warnForm(Form):
    reason = StringField('reason', validators=[InputRequired("Please enter your reason."), Length(max=255, message="Your reason cannot be longer than 255 characters.")])


class banForm(Form):
    reason = StringField('reason', validators=[InputRequired("Please enter your reason."), Length(max=255, message="Your reason cannot be longer than 255 characters.")])

# Password Reset Form --------------------------------------------------------------------------------------------------------

class passwordForm(Form):
    email = EmailField('email', validators=[InputRequired("Please enter your email address.")])

    def validate_email(self, field):
        email = self.email.data

        # If there is not an account with the email and it is not confirmed
        if db.session.query(User).filter_by(email=email, activated=True).count() != 1:
            # If email is present but not activated
            if db.session.query(User).filter_by(email=email, activated=False).count() > 0:
                raise ValidationError("The email associated with this account has not been confirmed.")
            # If email is not present
            else:
                raise ValidationError("There is no account with this email address.")

class resetPasswordForm(Form):
    password = PasswordField('password', validators=[InputRequired("Please enter a password."), Length(min=5, message="Your password must be at least 5 characters.")])

# Contact Form ---------------------------------------------------------------------------------------------------------------

class contactForm(Form):
    name = StringField('name', validators=[InputRequired("Please enter your name.")])
    email = EmailField('email', validators=[InputRequired("Please enter your email address."), Email("Please enter a valid email address.")])
    message = StringField('message', widget=TextArea(), validators=[InputRequired('Please enter your message.')])

# Settings Form --------------------------------------------------------------------------------------------------------------

def getPassword(form, field):
    try:
        password = checkPassword(current_user.id, field.data)
        if password is False:
            raise ValidationError('Your password is incorrect.')
    except:
        raise ValidationError('There is no password associated with your account. For security reasons, please add a password before deleting your account.')


class updateEmailForm(Form):
    email = EmailField('email', validators=[InputRequired("Please enter your email address."), Email("Please enter a valid email address.")])

    def validate_email(self, field):
        email = self.email.data
        if checkEmail(email):
            raise ValidationError("There is already an account with this email address.")


class changePasswordForm(Form):
    oldPassword = PasswordField('password', validators=[InputRequired("Please enter your current password."), getPassword])
    newPassword = PasswordField('password', validators=[InputRequired("Please enter your new password."), Length(min=5, message="Your new password must be at least 5 characters.")])


class deleteAccountForm(Form):
    password = PasswordField('password', validators=[InputRequired("Please enter the password to your account."), getPassword])
