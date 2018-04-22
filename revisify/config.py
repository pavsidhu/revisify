# Copyright (c) 2016 by Revisify. All Rights Reserved.


class Config(object):
    DEBUG = False
    SCREENSHOT = False

    SECRET_KEY = ''

    # Database migration
    MIGRATE_PRODUCTION = True

    # File storage i.e. user profile pictures
    S3BUCKET = ''

    MAIL_SECRET_KEY = ''
    MAIL_DEFAULT_SENDER = ''

    # This is used for social network sign in
    OAUTH_GOOGLE_ID = ''
    OAUTH_GOOGLE_SECRET = ''
    OAUTH_FACEBOOK_ID = ''
    OAUTH_FACEBOOK_SECRET = ''

    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''


class Development(Config):
    DEBUG = True

    SECRET_KEY = ''

    MIGRATE_PRODUCTION = False
    SQLALCHEMY_DATABASE_URI = ''

    MAIL_SECRET_KEY = ''
    MAIL_DEFAULT_SENDER = ''

    # OAuth2 usually only works on HTTPS for security, this allows it to work on HTTP
    OAUTHLIB_INSECURE_TRANSPORT = True

    OAUTH_GOOGLE_ID = ''
    OAUTH_GOOGLE_SECRET = ''
    OAUTH_FACEBOOK_ID = ''
    OAUTH_FACEBOOK_SECRET = ''


class Screenshot(Development):
    SCREENSHOT = True


class Testing(Config):
    pass


class Production(Config):
    SQLALCHEMY_DATABASE_URI = ''
    S3BUCKET = ''
