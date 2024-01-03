from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.utils import *

from api.permissions import HasAppAPIKey

from rest_framework import status
from django.db.models import Q

from core.utils import randomstr

from api.views.utils import *

from backend.models import *

import json
from django.utils import timezone
import datetime

import logging
logger = logging.getLogger('SimpleStart')

# Custom decorators
from backend.decorators import *

# Serializers
from api.serializers.app_serializers import *

# API documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.documentation.app_documentation import *
from api.documentation.common_elements import error_response, success_response


#-----------------------------------------------------------------------------------------------------------------------------
# Getting apps
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    tags=['Apps'],
    operation_id="Get App List",
    operation_description="Retrieve a list of apps",
    responses={
        200: app_list_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING),
        openapi.Parameter('sort', openapi.IN_QUERY, description="Sort option", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_apps(request):
    
    user = request.user

    # Filter apps based on app and status, using select_related for optimization
    app_users = AppUser.objects.filter(
        user=user,
        status='active',
    )
    app_ids = []
    for app_user in app_users:
        app_ids.append(app_user.app.app_id)
    query = App.objects.select_related('created_user').filter(app_id__in=app_ids, status='active').order_by('name')

    # Apply search filtering if applicable
    search_query = request.query_params.get('search', '').strip()
    if search_query:
        query = query.filter(Q(name__icontains=search_query))

    # Apply sorting
    sort_option = request.query_params.get('sort', '').strip()
    sort_fields = {
        'created_at_asc': 'created_at',
        'created_at_desc': '-created_at',
        'name_asc': 'name',
        'name_desc': '-name'
    }
    query = query.order_by(sort_fields.get(sort_option, 'name'))  # Default sort by name

    # Pagination
    try:
        page_number = int(request.query_params.get('page', 1))
    except ValueError:
        return Response({'errors': ['Page number must be an integer.']}, status=status.HTTP_400_BAD_REQUEST)
    try:
        page_size = int(request.query_params.get('page_size', 5))
        if page_size > 100:  # Check if page size is above 100
            return Response({'errors': ['Page size cannot exceed 100.']}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'errors': ['Page size must be an integer.']}, status=status.HTTP_400_BAD_REQUEST)
    paginator = Paginator(query, page_size)
    
    try:
        apps = paginator.page(page_number)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)

    serializer = AppSerializer(apps, many=True)
    response_data = {
        'apps': serializer.data,
        'page': apps.number,
        'pages': paginator.num_pages,
        'records_count': paginator.count
    }

    return Response(response_data)

@swagger_auto_schema(
    method='get',
    tags=['Apps'],
    operation_id="Get App",
    operation_description="Retrieve a app",
    responses={
        200: app_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@validate_app_user
def get_app(request, app_id):

    user = request.user
    app = request.app

    serializer = AppSerializer(app, many=False)
    return Response({'app': serializer.data})


#-----------------------------------------------------------------------------------------------------------------------------
# Adding apps
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Apps'],
    operation_id="Add App",
    operation_description="Add a app",
    request_body=app_add_schema,
    responses={
        201: app_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_app(request):
    app_object = request.data
    user = request.user
    
    valid_params = check_params(app_object, [
        {'param': 'app_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])
    
    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = create_app_record(app_object, request.user)
            serializer = AppSerializer(result['app'])
            return Response({'app': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating app: {e}')
            return Response({'errors': ['Failed to create app.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Apps'],
    operation_id="Add Apps",
    operation_description="Add a list of apps",
    request_body=app_add_request_body,
    responses={
        200: add_apps_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_apps(request):
    data = request.data
    
    apps_data = data.get('apps')
    if not isinstance(apps_data, list) or not apps_data:
        return Response({'errors': ['Apps list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(apps_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'apps_added': [], 'apps_not_added': []}

    try:
        with transaction.atomic():
            for index, app_object in enumerate(apps_data):
                valid_params = check_params(app_object, [
                    {'param': 'app_id', 'type': 'string', 'required': False, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    result = create_app_record(app_object, request.user)
                    serializer = AppSerializer(result['app'])
                    response_data['apps_added'].append(serializer.data)
                else:
                    response_data['apps_not_added'].append({
                        'index': index,
                        'submitted_object': app_object,
                        'errors': valid_params['errors']
                    })
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error adding apps: {e}')
        return Response({'errors': ['Failed to add apps.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Updating apps
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Apps'],
    operation_id="Update App",
    operation_description="Update a app",
    request_body=app_update_schema,
    responses={
        201: app_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@validate_app_user
def update_app(request, app_id):
    app_object = request.data
    user = request.user
    app = request.app
    
    valid_params = check_params(app_object, [
        {'param': 'app_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])

    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = update_app_record(app, app_object)
            serializer = AppSerializer(result['app'])
            return Response({'app': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating app: {e}')
            return Response({'errors': ['Failed to update app.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['Apps'],
    operation_id="Update Apps",
    operation_description="Update a list of apps",
    request_body=app_update_request_body,
    responses={
        200: update_apps_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_apps(request):
    data = request.data

    apps_data = data.get('apps')
    if not isinstance(apps_data, list) or not apps_data:
        return Response({'errors': ['Apps list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(apps_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'apps_updated': [], 'apps_not_updated': []}

    try:
        with transaction.atomic():
            for index, app_object in enumerate(apps_data):
                valid_params = check_params(app_object, [
                    {'param': 'app_id', 'type': 'string', 'required': True, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    app_id = app_object['app_id']
                    try:
                        app = App.objects.get(app_id=app_id, status="active")
                        result = update_app_record(app, app_object)
                        serializer = AppSerializer(result['app'])
                        response_data['apps_updated'].append(serializer.data)
                    except App.DoesNotExist:
                        response_data['apps_not_updated'].append({
                            'index': index,
                            'submitted_object': app_object,
                            'errors': ['App not found']
                        })
                else:
                    response_data['apps_not_updated'].append({
                        'index': index,
                        'submitted_object': app_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error updating apps: {e}')
        return Response({'errors': ['Failed to update apps.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#-----------------------------------------------------------------------------------------------------------------------------
# Archiving apps
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Apps'],
    operation_id="Archive App",
    operation_description="Archive a app",
    responses={
        201: app_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@validate_app_user
def archive_app(request, app_id):
    app = request.app

    try:
        with transaction.atomic():
            app.status = "archived"
            app.save()
        serializer = AppSerializer(app)
        return Response({'app': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving app: {e}')
        return Response({'errors': ['Failed to archive app.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Apps'],
    operation_id="Archive Apps",
    operation_description="Archive a list of apps",
    request_body=app_archive_request_body,
    responses={
        200: archive_apps_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archive_apps(request):
    data = request.data

    apps_data = data.get('apps')
    if not isinstance(apps_data, list) or not apps_data:
        return Response({'errors': ['Apps list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(apps_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'apps_archived': [], 'apps_not_archived': []}

    try:
        with transaction.atomic():
            for index, app_object in enumerate(apps_data):
                valid_params = check_params(app_object, [
                    {'param': 'app_id', 'type': 'string', 'required': True, 'length': 32},
                ])

                if valid_params['valid']:
                    app_id = app_object['app_id']
                    try:
                        app = App.objects.get(app_id=app_id, status="active")
                        app.status = "archived"
                        app.save()
                        serializer = AppSerializer(app)
                        response_data['apps_archived'].append(serializer.data)
                    except App.DoesNotExist:
                        response_data['apps_not_archived'].append({
                            'index': index,
                            'submitted_object': app_object,
                            'errors': ['App not found']
                        })
                else:
                    response_data['apps_not_archived'].append({
                        'index': index,
                        'submitted_object': app_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving apps: {e}')
        return Response({'errors': ['Failed to archive apps.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Apps'],
    operation_id="Destroy Apps",
    operation_description="Destroy and archive all apps",
    request_body=None,
    responses={
        200: destroy_apps_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def destroy_apps(request):
    user = request.user

    # Fetching apps that the user has access to and are active
    app_users = AppUser.objects.filter(user=user, status='active')
    app_ids = [app_user.app.app_id for app_user in app_users]
    apps = App.objects.filter(app_id__in=app_ids, status='active')

    if not apps:
        return Response({'errors': ['No active apps found for the user.']}, status=status.HTTP_400_BAD_REQUEST)

    # Update the status of each app to 'archived'
    for app in apps:
        app.status = 'archived'

    try:
        with transaction.atomic():
            App.objects.bulk_update(apps, ['status'])
        serializer = AppSerializer(apps, many=True)
        return Response({'apps_archived': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error destroying apps: {e}')
        return Response({'errors': ['Failed to destroy apps.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Export apps
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Apps'],
    operation_id="Export Apps",
    operation_description="Export app data to a flat file",
    request_body=None,
    responses={
        202: success_response,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_apps(request):
    user = request.user

    # Get data elements for search, filters, date ranges, etc here

    # Query the data needed here

    # Initiate the background task for exporting

    return Response({'message': 'Export initiated'}, status=status.HTTP_202_ACCEPTED)


#-----------------------------------------------------------------------------------------------------------------------------
# Utils apps
#-----------------------------------------------------------------------------------------------------------------------------

def create_app_record(data, user):
    try:
        app_id = data.get('app_id', randomstr())

        app_data = {
            'app_id': app_id,
            'name': data['name'],
            'created_user': user,
            'data': data.get('data'),
            'config': data.get('config'),
        }

        # Remove None values from dictionary
        app_data = {k: v for k, v in app_data.items() if v is not None}

        app = App.objects.create(**app_data)

        # Create the app user
        app_user = AppUser()
        app_user.app_user_id = randomstr()
        app_user.user = user
        app_user.email = user.email
        app_user.app = app
        app_user.role = 'admin'
        app_user.save()

        return {
            'success': True,
            'app': app,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error creating the app record'],
        }


def update_app_record(app, data):
    try:
        updated_fields = []

        for field in ['name', 'data', 'config']:
            if field in data:
                setattr(app, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            app.save(update_fields=updated_fields)

        return {
            'success': True,
            'app': app,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error updating the app record'],
        }