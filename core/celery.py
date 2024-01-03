from __future__ import absolute_import
import os
import ssl
import django
from celery import Celery
from celery import shared_task
from django.conf import settings
from celery.schedules import crontab
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import utc
import random
import datetime
from django.conf import settings


# Setup django and celery to work with tasks and models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings')

# ------------------------------------------------------------------------------



