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
logger = logging.getLogger('SimpleAg')

# Custom decorators
from backend.decorators import *

# Serializers
from api.serializers.profile_serializers import *

# API documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.documentation.profile_documentation import *
from api.documentation.common_elements import error_response, success_response


#-----------------------------------------------------------------------------------------------------------------------------
# Getting profiles
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    tags=['Profiles'],
    operation_id="Get Profile List",
    operation_description="Retrieve a list of profiles",
    responses={
        200: profile_list_response_schema,
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
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def get_profiles(request, app_id):
    
    user = request.user
    app = request.app

    # Filter profiles based on app and status, using select_related for optimization
    query = Profile.objects.select_related('app', 'created_user').filter(app=app, status='active')

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
        profiles = paginator.page(page_number)
    except PageNotAnInteger:
        profiles = paginator.page(1)
    except EmptyPage:
        profiles = paginator.page(paginator.num_pages)

    serializer = ProfileSerializer(profiles, many=True)
    response_data = {
        'profiles': serializer.data,
        'page': profiles.number,
        'pages': paginator.num_pages,
        'records_count': paginator.count
    }

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    tags=['Profiles'],
    operation_id="Get Profile",
    operation_description="Retrieve a profile",
    responses={
        200: profile_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[]
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_profile
def get_profile(request, app_id, profile_id):

    user = request.user
    app = request.app
    profile = request.profile

    serializer = ProfileSerializer(profile, many=False)
    return Response({'profile': serializer.data})



#-----------------------------------------------------------------------------------------------------------------------------
# Adding profiles
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Profiles'],
    operation_id="Add Profile",
    operation_description="Add a profile",
    request_body=profile_add_schema,
    responses={
        201: profile_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_profile(request, app_id):
    profile_object = request.data
    user = request.user
    app = request.app
    
    valid_params = check_params(profile_object, [
        {'param': 'profile_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])
    
    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = create_profile_record(profile_object, app, request.user)
            serializer = ProfileSerializer(result['profile'])
            return Response({'profile': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating profile: {e}')
            return Response({'errors': ['Failed to create profile.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Profiles'],
    operation_id="Add Profiles",
    operation_description="Add a list of profiles",
    request_body=profile_add_request_body,
    responses={
        200: add_profiles_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_profiles(request, app_id):
    data = request.data
    app = request.app

    profiles_data = data.get('profiles')
    if not isinstance(profiles_data, list) or not profiles_data:
        return Response({'errors': ['Profiles list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(profiles_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'profiles_added': [], 'profiles_not_added': []}

    try:
        with transaction.atomic():
            for index, profile_object in enumerate(profiles_data):
                valid_params = check_params(profile_object, [
                    {'param': 'profile_id', 'type': 'string', 'required': False, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    result = create_profile_record(profile_object, app, request.user)
                    serializer = ProfileSerializer(result['profile'])
                    response_data['profiles_added'].append(serializer.data)
                else:
                    response_data['profiles_not_added'].append({
                        'index': index,
                        'submitted_object': profile_object,
                        'errors': valid_params['errors']
                    })
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error adding profiles: {e}')
        return Response({'errors': ['Failed to add profiles.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Updating profiles
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Profiles'],
    operation_id="Update Profile",
    operation_description="Update a profile",
    request_body=profile_update_schema,
    responses={
        201: profile_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_profile
def update_profile(request, app_id, profile_id):
    profile_object = request.data
    user = request.user
    app = request.app
    profile = request.profile
    
    valid_params = check_params(profile_object, [
        {'param': 'profile_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])

    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = update_profile_record(app, profile, profile_object)
            serializer = ProfileSerializer(result['profile'])
            return Response({'profile': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating profile: {e}')
            return Response({'errors': ['Failed to update profile.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['Profiles'],
    operation_id="Update Profiles",
    operation_description="Update a list of profiles",
    request_body=profile_update_request_body,
    responses={
        200: update_profiles_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def update_profiles(request, app_id):
    data = request.data
    app = request.app

    profiles_data = data.get('profiles')
    if not isinstance(profiles_data, list) or not profiles_data:
        return Response({'errors': ['Profiles list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(profiles_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'profiles_updated': [], 'profiles_not_updated': []}

    try:
        with transaction.atomic():
            for index, profile_object in enumerate(profiles_data):
                valid_params = check_params(profile_object, [
                    {'param': 'profile_id', 'type': 'string', 'required': True, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    profile_id = profile_object['profile_id']
                    try:
                        profile = Profile.objects.get(profile_id=profile_id, app=app, status="active")
                        result = update_profile_record(app, profile, profile_object)
                        serializer = ProfileSerializer(result['profile'])
                        response_data['profiles_updated'].append(serializer.data)
                    except Profile.DoesNotExist:
                        response_data['profiles_not_updated'].append({
                            'index': index,
                            'submitted_object': profile_object,
                            'errors': ['Profile not found']
                        })
                else:
                    response_data['profiles_not_updated'].append({
                        'index': index,
                        'submitted_object': profile_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error updating profiles: {e}')
        return Response({'errors': ['Failed to update profiles.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#-----------------------------------------------------------------------------------------------------------------------------
# Archiving profiles
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Profiles'],
    operation_id="Archive Profile",
    operation_description="Archive a profile",
    responses={
        201: profile_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_profile
def archive_profile(request, app_id, profile_id):
    app = request.app
    profile = request.profile

    try:
        with transaction.atomic():
            profile.status = "archived"
            profile.save()
        serializer = ProfileSerializer(profile)
        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving profile: {e}')
        return Response({'errors': ['Failed to archive profile.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Profiles'],
    operation_id="Archive Profiles",
    operation_description="Archive a list of profiles",
    request_body=profile_archive_request_body,
    responses={
        200: archive_profiles_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def archive_profiles(request, app_id):
    data = request.data
    app = request.app

    profiles_data = data.get('profiles')
    if not isinstance(profiles_data, list) or not profiles_data:
        return Response({'errors': ['Profiles list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(profiles_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'profiles_archived': [], 'profiles_not_archived': []}

    try:
        with transaction.atomic():
            for index, profile_object in enumerate(profiles_data):
                valid_params = check_params(profile_object, [
                    {'param': 'profile_id', 'type': 'string', 'required': True, 'length': 32},
                ])

                if valid_params['valid']:
                    profile_id = profile_object['profile_id']
                    try:
                        profile = Profile.objects.get(profile_id=profile_id, app=app, status="active")
                        profile.status = "archived"
                        profile.save()
                        serializer = ProfileSerializer(profile)
                        response_data['profiles_archived'].append(serializer.data)
                    except Profile.DoesNotExist:
                        response_data['profiles_not_archived'].append({
                            'index': index,
                            'submitted_object': profile_object,
                            'errors': ['Profile not found']
                        })
                else:
                    response_data['profiles_not_archived'].append({
                        'index': index,
                        'submitted_object': profile_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving profiles: {e}')
        return Response({'errors': ['Failed to archive profiles.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Profiles'],
    operation_id="Destroy Profiles",
    operation_description="Destroy and archive all profiles",
    request_body=None,
    responses={
        200: destroy_profiles_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def destroy_profiles(request, app_id):
    user = request.user 
    app = request.app
    
    # Fetching apps that the user has access to and are active
    profiles = Profile.objects.filter(app=app, status='active')

    if not profiles:
        return Response({'errors': ['No active profiles.']}, status=status.HTTP_400_BAD_REQUEST)

    # Update the status of each app to 'archived'
    for profile in profiles:
        profile.status = 'archived'

    try:
        with transaction.atomic():
            Profile.objects.bulk_update(profiles, ['status'])
        serializer = ProfileSerializer(profiles, many=True)
        return Response({'profiles_archived': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error destroying profiles: {e}')
        return Response({'errors': ['Failed to destroy profiles.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Export profiles
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Profiles'],
    operation_id="Export Profiles",
    operation_description="Export profile data to a flat file",
    request_body=None,
    responses={
        202: success_response,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def export_profiles(request, app_id):
    user = request.user
    app = request.app

    # Get data elements for search, filters, date ranges, etc here

    # Query the data needed here

    # Initiate the background task for exporting

    return Response({'message': 'Export initiated'}, status=status.HTTP_202_ACCEPTED)


#-----------------------------------------------------------------------------------------------------------------------------
# Utils profiles
#-----------------------------------------------------------------------------------------------------------------------------

def create_profile_record(data,  app, user):
    try:
        profile_id = data.get('profile_id', randomstr())

        profile_data = {
            'profile_id': profile_id,
            'name': data['name'],
            'app': app,
            'created_user': user,
            'data': data.get('data'),
            'config': data.get('config'),
        }

        # Remove None values from dictionary
        profile_data = {k: v for k, v in profile_data.items() if v is not None}

        profile = Profile.objects.create(**profile_data)

        return {
            'success': True,
            'profile': profile,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error creating the profile record'],
        }


def update_profile_record(app, profile, data):
    try:
        updated_fields = []

        for field in ['name', 'data', 'config']:
            if field in data:
                setattr(profile, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            profile.save(update_fields=updated_fields)

        return {
            'success': True,
            'profile': profile,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error updating the profile record'],
        }