from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.utils.text import slugify
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import time
import json

from django.conf import settings
from django.db.models import Q

from backend.models import *
from core.utils import *
from backend.utils import *
from messaging.tasks import *


def is_admin(app_user):
    is_admin = False
    if app_user.role == 'admin':
        is_admin = True
    return is_admin