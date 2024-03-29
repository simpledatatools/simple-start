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


#-----------------------------------------------------------------------------------------------------------------------------
# Datasets
#-----------------------------------------------------------------------------------------------------------------------------

def validate_dataset(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        app_id = kwargs.get('app_id')
        dataset_id = kwargs.get('dataset_id')
        user = request.user

        dataset = Dataset.objects.filter(dataset_id=dataset_id, app__app_id=app_id, status="active", app__status="active").first()
        if not dataset:
            return Response({'errors': ['Dataset does not exist']}, status=status.HTTP_400_BAD_REQUEST)

        # Add app and app_user to request for later use
        request.dataset = dataset

        return func(request, *args, **kwargs)
    return decorator