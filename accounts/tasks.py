from celery import shared_task

from django.core.files.base import ContentFile

from backend.models import *
from backend.tasks import *
from core.utils import randompassword, randomstr

from core.utils import randomlongstr

from messaging.mail_utils import *
from core.utils import *

