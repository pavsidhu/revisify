# Copyright (c) 2016 by Revisify. All Rights Reserved.

import calendar
import flask_sijax
import jinja2
import os
import re

from flask import Markup
from bleach import clean
from datetime import datetime

def configureJinja(app, version):

    # Removes whitespace from rendered HTML
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Allows Jinja to execute python code. This is bad practice since it blurs
    # the line between back-end and front-end code. Only use this as a last
    # resort.
    app.jinja_env.add_extension('jinja2.ext.do')

    # These variables can be accessed from any template
    app.jinja_env.globals.update({
        'year': datetime.today().year,
        'version': version,
        'debug': app.config['DEBUG'],
        'screenshot': app.config['SCREENSHOT'],
    })

    @app.template_filter('safeJavascript')
    def safeJavascript(value):
        if not value:
            return ''
        value = value.replace('\n', ' ').replace('\r', ' ') # Remove line breaks
        newValue = ''
        for char in value:
            if char == '\'':
                newValue += '\\\''
            else:
                newValue += char
        return newValue


    # Gets first character - first letter or if no letters first character
    @app.template_filter('firstChar')
    def firstChar(value):
        value = value.upper()
        string = re.search('[A-Z]', value)
        stringNum = re.search('[A-Z0-9]', value)
        try:
            return string.group(0)
        except:
            try:
                return stringNum.group(0)
            except:
                return value[0:1:]


    # Formats date from "2016-11-06" to "06 November 2016"
    @app.template_filter('formatDate')
    def formatDate(value):
        # Get year
        year = str(value)[0:4]

        # Get month number and remove leading zeros
        monthNumber = str(value)[5:7].lstrip('0')

        # Convert to month name
        month = calendar.month_name[int(monthNumber)]

        # Get day number and remove leading zeros
        day = str(value)[8:10].lstrip('0')

        # Put it all together
        value = day + ' ' + month + ' ' + year
        return value


    # Formats date from "2016-11-06" to "Nov 06"
    @app.template_filter('shortFormatDate')
    def shortFormatDate(value):
        date = formatDate(value).split()
        return date[1][0:3] + ' ' + date[0]

    # Cleans up HTML, removing unneeded tags
    @app.template_filter('bleach')
    def bleach(value):
        return clean(Markup(value), strip=True)
