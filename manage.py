# Copyright (c) 2016 by Revisify. All Rights Reserved.

from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from revisify import createApp as app

manager = Manager(app)
manager.add_option('-c', '--config', dest='configuration', required=False, help="Configuration choices: development, testing, production.")
manager.add_command('db', MigrateCommand)

manager.run()
