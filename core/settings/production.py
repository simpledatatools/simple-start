from __future__ import absolute_import, unicode_literals
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

import dj_database_url
DATABASES['default'] = dj_database_url.config()

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [
    os.environ['HOST_URL'],
    os.environ['ACCESS_URL']
]

# Redirect to https in production
SECURE_SSL_REDIRECT = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400 #10MB limit

# CELERY STUFF
REDIS_URL = os.environ['REDIS_URL']
BROKER_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL']

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
BASE_URL = os.environ['BASE_URL']