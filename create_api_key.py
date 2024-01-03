import sys
import json
import os
import django
from django.utils import timezone
import random
from itertools import chain
import pytz

import logging
logger = logging.getLogger('SimpleAg')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import *
from backend.models import *
from core.utils import *

# AS Channels
app = App.objects.filter(app_id='t9wH6RI5HnOFJcsQ').first()
user = CustomUser.objects.filter(email="matt@simpledatatools.com").first()

name, key = AppAPIKey.objects.create_key(
    app=app,
    user=user,
    name="App Key 1"
)
logger.info(name)
logger.info(key)

count = AppAPIKey.objects.count()
logger.info(count)

api_key = AppAPIKey.objects.get_from_key(key)
app = api_key.app
user = api_key.user
logger.info(app.name)
logger.info(user.email)

# App: t9wH6RI5HnOFJcsQ
# lHvZBCpG.8TOMTegKwg2RzBWEZ7rztJTrk2X7OANj