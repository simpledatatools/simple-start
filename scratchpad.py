
import sys
import json
import os
import django
from django.utils import timezone
import random

import datetime
from datetime import timedelta

from openpyxl import Workbook
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Font

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import logging
logger = logging.getLogger('SimpleStart')

from backend.models import *
from core.utils import *
from accounts.models import *
