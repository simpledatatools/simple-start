from rest_framework_api_key.permissions import BaseHasAPIKey
from backend.models import AppAPIKey

class HasAppAPIKey(BaseHasAPIKey):
    model = AppAPIKey
