from django.apps import apps
import json
from accounts.models import *
from core.utils import *
from backend.models import *
from backend.utils import *

import datetime

import logging
logger = logging.getLogger('SimpleStart')

from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from backend.models import AppAPIKey  # Update with correct import

class IsAuthenticatedOrHasAPIKey(permissions.BasePermission):
    """
    Allows access to authenticated users or users with a valid API key.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated via JWT
        if request.user and request.user.is_authenticated:
            return True

        # Check for API Key in the Authorization header
        key_request = request.META.get("HTTP_AUTHORIZATION")
        if key_request:
            try:
                key = key_request.split()[1]
                api_key = AppAPIKey.objects.get_from_key(key)
                if api_key:
                    # Attach the user associated with the API key to the request
                    request.user = api_key.user
                    return True
            except AppAPIKey.DoesNotExist:
                pass  # API Key is not valid

        # Neither JWT nor API Key is valid
        return False


def check_params(data, params):
    valid = True
    errors = []

    # Mapping of type strings to actual Python types
    type_mapping = {
        'string': str,
        'integer': int,
        'float': float,
        'object_list': list,
        'string_list': list,
        'boolean': bool,
        'object': dict,
        'date': dict,
        'relation': (str, int)  # Assuming relation can be string or integer
    }

    # Function to validate individual parameter
    def validate_param(param_name, param_object, param_value):
        nonlocal errors

        expected_type = type_mapping[param_object['type']]

        valid = True
        
        # Type validation
        if not isinstance(param_value, expected_type):
            errors.append(f'Parameter: {param_name} is not of type {param_object["type"]}')
            valid = False

        # Additional validations based on type
        if param_object['type'] == 'string':
            if param_value.strip() == '':
                errors.append(f'Empty parameter: {param_name}')
                valid = False

            if 'length' in param_object and len(param_value) > param_object['length']:
                errors.append(f'Parameter: {param_name} exceeds allowed length of {param_object["length"]}')
                valid = False

            if 'options' in param_object and param_value not in param_object['options']:
                errors.append(f'Parameter: {param_name} does not have a valid option from values {param_object["options"]}')
                valid = False
        
        if param_object['type'] == 'object_list' or param_object['type'] == 'string_list':
            if len(param_value) == 0:
                errors.append(f'Parameter {param_name} cannot be an empty list')
                valid = False

        if param_object['type'] == 'date':
            try:
                datetime.datetime(param_value['year'], param_value['month'], param_value['day'])
            except (ValueError, KeyError):
                errors.append(f'Parameter: {param_name} - included year, month, and day is not a valid date')
                valid = False

        return valid

    # Iterate over each expected parameter
    for param_object in params:
        param_name = param_object['param']

        # Required parameter check
        if param_object['required'] and param_name not in data:
            errors.append(f'Missing parameter: {param_name}')
            valid = False

        # Validate the parameter if it exists
        if param_name in data:
            if not validate_param(param_name, param_object, data[param_name]):
                valid = False

    # Check for unrecognized parameters
    recognized_params = {param['param'] for param in params}
    unrecognized_params = set(data.keys()) - recognized_params
    for param in unrecognized_params:
        errors.append(f'Parameter not valid: {param}')
        valid = False

    return {'valid': valid, 'errors': errors}