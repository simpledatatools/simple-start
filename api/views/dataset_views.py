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
from api.serializers.dataset_serializers import *

# API documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.documentation.dataset_documentation import *
from api.documentation.common_elements import error_response, success_response


#-----------------------------------------------------------------------------------------------------------------------------
# Getting datasets
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    tags=['Datasets'],
    operation_id="Get Dataset List",
    operation_description="Retrieve a list of datasets",
    responses={
        200: dataset_list_response_schema,
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
def get_datasets(request, app_id):
    
    user = request.user
    app = request.app

    # Filter datasets based on app and status, using select_related for optimization
    query = Dataset.objects.select_related('app', 'created_user').filter(app=app, status='active')

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
        datasets = paginator.page(page_number)
    except PageNotAnInteger:
        datasets = paginator.page(1)
    except EmptyPage:
        datasets = paginator.page(paginator.num_pages)

    serializer = DatasetSerializer(datasets, many=True)
    response_data = {
        'datasets': serializer.data,
        'page': datasets.number,
        'pages': paginator.num_pages,
        'records_count': paginator.count
    }

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    tags=['Datasets'],
    operation_id="Get Dataset",
    operation_description="Retrieve a dataset",
    responses={
        200: dataset_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[]
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_dataset
def get_dataset(request, app_id, dataset_id):

    user = request.user
    app = request.app
    dataset = request.dataset

    serializer = DatasetSerializer(dataset, many=False)
    return Response({'dataset': serializer.data})



#-----------------------------------------------------------------------------------------------------------------------------
# Adding datasets
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Datasets'],
    operation_id="Add Dataset",
    operation_description="Add a dataset",
    request_body=dataset_add_schema,
    responses={
        201: dataset_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_dataset(request, app_id):
    dataset_object = request.data
    user = request.user
    app = request.app
    
    valid_params = check_params(dataset_object, [
        {'param': 'dataset_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])
    
    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = create_dataset_record(dataset_object, app, request.user)
            serializer = DatasetSerializer(result['dataset'])
            return Response({'dataset': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dataset: {e}')
            return Response({'errors': ['Failed to create dataset.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Datasets'],
    operation_id="Add Datasets",
    operation_description="Add a list of datasets",
    request_body=dataset_add_request_body,
    responses={
        200: add_datasets_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_datasets(request, app_id):
    data = request.data
    app = request.app

    datasets_data = data.get('datasets')
    if not isinstance(datasets_data, list) or not datasets_data:
        return Response({'errors': ['Datasets list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(datasets_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'datasets_added': [], 'datasets_not_added': []}

    try:
        with transaction.atomic():
            for index, dataset_object in enumerate(datasets_data):
                valid_params = check_params(dataset_object, [
                    {'param': 'dataset_id', 'type': 'string', 'required': False, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    result = create_dataset_record(dataset_object, app, request.user)
                    serializer = DatasetSerializer(result['dataset'])
                    response_data['datasets_added'].append(serializer.data)
                else:
                    response_data['datasets_not_added'].append({
                        'index': index,
                        'submitted_object': dataset_object,
                        'errors': valid_params['errors']
                    })
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error adding datasets: {e}')
        return Response({'errors': ['Failed to add datasets.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Updating datasets
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Datasets'],
    operation_id="Update Dataset",
    operation_description="Update a dataset",
    request_body=dataset_update_schema,
    responses={
        201: dataset_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_dataset
def update_dataset(request, app_id, dataset_id):
    dataset_object = request.data
    user = request.user
    app = request.app
    dataset = request.dataset
    
    valid_params = check_params(dataset_object, [
        {'param': 'dataset_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])

    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = update_dataset_record(app, dataset, dataset_object)
            serializer = DatasetSerializer(result['dataset'])
            return Response({'dataset': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating dataset: {e}')
            return Response({'errors': ['Failed to update dataset.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['Datasets'],
    operation_id="Update Datasets",
    operation_description="Update a list of datasets",
    request_body=dataset_update_request_body,
    responses={
        200: update_datasets_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def update_datasets(request, app_id):
    data = request.data
    app = request.app

    datasets_data = data.get('datasets')
    if not isinstance(datasets_data, list) or not datasets_data:
        return Response({'errors': ['Datasets list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(datasets_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'datasets_updated': [], 'datasets_not_updated': []}

    try:
        with transaction.atomic():
            for index, dataset_object in enumerate(datasets_data):
                valid_params = check_params(dataset_object, [
                    {'param': 'dataset_id', 'type': 'string', 'required': True, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    dataset_id = dataset_object['dataset_id']
                    try:
                        dataset = Dataset.objects.get(dataset_id=dataset_id, app=app, status="active")
                        result = update_dataset_record(app, dataset, dataset_object)
                        serializer = DatasetSerializer(result['dataset'])
                        response_data['datasets_updated'].append(serializer.data)
                    except Dataset.DoesNotExist:
                        response_data['datasets_not_updated'].append({
                            'index': index,
                            'submitted_object': dataset_object,
                            'errors': ['Dataset not found']
                        })
                else:
                    response_data['datasets_not_updated'].append({
                        'index': index,
                        'submitted_object': dataset_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error updating datasets: {e}')
        return Response({'errors': ['Failed to update datasets.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#-----------------------------------------------------------------------------------------------------------------------------
# Archiving datasets
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Datasets'],
    operation_id="Archive Dataset",
    operation_description="Archive a dataset",
    responses={
        201: dataset_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_dataset
def archive_dataset(request, app_id, dataset_id):
    app = request.app
    dataset = request.dataset

    try:
        with transaction.atomic():
            dataset.status = "archived"
            dataset.save()
        serializer = DatasetSerializer(dataset)
        return Response({'dataset': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving dataset: {e}')
        return Response({'errors': ['Failed to archive dataset.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Datasets'],
    operation_id="Archive Datasets",
    operation_description="Archive a list of datasets",
    request_body=dataset_archive_request_body,
    responses={
        200: archive_datasets_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def archive_datasets(request, app_id):
    data = request.data
    app = request.app

    datasets_data = data.get('datasets')
    if not isinstance(datasets_data, list) or not datasets_data:
        return Response({'errors': ['Datasets list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(datasets_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'datasets_archived': [], 'datasets_not_archived': []}

    try:
        with transaction.atomic():
            for index, dataset_object in enumerate(datasets_data):
                valid_params = check_params(dataset_object, [
                    {'param': 'dataset_id', 'type': 'string', 'required': True, 'length': 32},
                ])

                if valid_params['valid']:
                    dataset_id = dataset_object['dataset_id']
                    try:
                        dataset = Dataset.objects.get(dataset_id=dataset_id, app=app, status="active")
                        dataset.status = "archived"
                        dataset.save()
                        serializer = DatasetSerializer(dataset)
                        response_data['datasets_archived'].append(serializer.data)
                    except Dataset.DoesNotExist:
                        response_data['datasets_not_archived'].append({
                            'index': index,
                            'submitted_object': dataset_object,
                            'errors': ['Dataset not found']
                        })
                else:
                    response_data['datasets_not_archived'].append({
                        'index': index,
                        'submitted_object': dataset_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving datasets: {e}')
        return Response({'errors': ['Failed to archive datasets.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Datasets'],
    operation_id="Destroy Datasets",
    operation_description="Destroy and archive all datasets",
    request_body=None,
    responses={
        200: destroy_datasets_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def destroy_datasets(request, app_id):
    user = request.user 
    app = request.app
    
    # Fetching apps that the user has access to and are active
    datasets = Dataset.objects.filter(app=app, status='active')

    if not datasets:
        return Response({'errors': ['No active datasets.']}, status=status.HTTP_400_BAD_REQUEST)

    # Update the status of each app to 'archived'
    for dataset in datasets:
        dataset.status = 'archived'

    try:
        with transaction.atomic():
            Dataset.objects.bulk_update(datasets, ['status'])
        serializer = DatasetSerializer(datasets, many=True)
        return Response({'datasets_archived': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error destroying datasets: {e}')
        return Response({'errors': ['Failed to destroy datasets.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Export datasets
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Datasets'],
    operation_id="Export Datasets",
    operation_description="Export dataset data to a flat file",
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
def export_datasets(request, app_id):
    user = request.user
    app = request.app

    # Get data elements for search, filters, date ranges, etc here

    # Query the data needed here

    # Initiate the background task for exporting

    return Response({'message': 'Export initiated'}, status=status.HTTP_202_ACCEPTED)


#-----------------------------------------------------------------------------------------------------------------------------
# Utils datasets
#-----------------------------------------------------------------------------------------------------------------------------

def create_dataset_record(data,  app, user):
    try:
        dataset_id = data.get('dataset_id', randomstr())

        dataset_data = {
            'dataset_id': dataset_id,
            'name': data['name'],
            'app': app,
            'created_user': user,
            'data': data.get('data'),
            'config': data.get('config'),
        }

        # Remove None values from dictionary
        dataset_data = {k: v for k, v in dataset_data.items() if v is not None}

        dataset = Dataset.objects.create(**dataset_data)

        return {
            'success': True,
            'dataset': dataset,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error creating the dataset record'],
        }


def update_dataset_record(app, dataset, data):
    try:
        updated_fields = []

        for field in ['name', 'data', 'config']:
            if field in data:
                setattr(dataset, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            dataset.save(update_fields=updated_fields)

        return {
            'success': True,
            'dataset': dataset,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error updating the dataset record'],
        }