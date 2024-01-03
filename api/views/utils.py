from django.apps import apps
import json
from accounts.models import *
from core.utils import *
from backend.models import *
from backend.utils import *

import datetime

import logging
logger = logging.getLogger('SimpleStart')

def check_request(request, app_id):
    
    user = None
    app = None
    api_key = None
    valid_user = False
    
    if not request.user.is_anonymous:
        user = request.user
        valid_user = True
    else: # The request is from the API_Key
        key_request = request.META["HTTP_AUTHORIZATION"]
        if key_request:
            key = key_request.split()[1]
            if key:
                api_key = AppAPIKey.objects.get_from_key(key)
                app = api_key.app
                user = api_key.user
                if app_id:
                    if app.app_id == app_id:
                        valid_user = True
                else:
                    valid_user = True
    
    request_data = {
        'valid': valid_user,
        'user': user,
        'app': app,
        'api_key': api_key,
    }

    return request_data