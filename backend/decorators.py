from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from backend.models import *

#-----------------------------------------------------------------------------------------------------------------------------
# App and app users
#-----------------------------------------------------------------------------------------------------------------------------

def validate_app_user(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        app_id = kwargs.get('app_id')
        user = request.user

        app = App.objects.filter(app_id=app_id, status="active").first()
        if not app:
            return Response({'errors': ['App does not exist']}, status=status.HTTP_400_BAD_REQUEST)
        
        app_user = AppUser.objects.filter(app=app, user=user, status="active").first()
        if not app_user:
            return Response({'errors': ['User is not authorized for this app']}, status=status.HTTP_403_FORBIDDEN)
        
        # Add app and app_user to request for later use
        request.app = app
        request.app_user = app_user

        return func(request, *args, **kwargs)
    return decorator