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
from api.serializers.customer_serializers import *

# API documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.documentation.customer_documentation import *
from api.documentation.common_elements import error_response, success_response


#-----------------------------------------------------------------------------------------------------------------------------
# Getting customers
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    tags=['Customers'],
    operation_id="Get Customer List",
    operation_description="Retrieve a list of customers",
    responses={
        200: customer_list_response_schema,
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
def get_customers(request, app_id):
    
    user = request.user
    app = request.app

    # Filter customers based on app and status, using select_related for optimization
    query = Customer.objects.select_related('app', 'created_user').filter(app=app, status='active')

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
        customers = paginator.page(page_number)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    serializer = CustomerSerializer(customers, many=True)
    response_data = {
        'customers': serializer.data,
        'page': customers.number,
        'pages': paginator.num_pages,
        'records_count': paginator.count
    }

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    tags=['Customers'],
    operation_id="Get Customer",
    operation_description="Retrieve a customer",
    responses={
        200: customer_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[]
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_customer
def get_customer(request, app_id, customer_id):

    user = request.user
    app = request.app
    customer = request.customer

    serializer = CustomerSerializer(customer, many=False)
    return Response({'customer': serializer.data})



#-----------------------------------------------------------------------------------------------------------------------------
# Adding customers
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_id="Add Customer",
    operation_description="Add a customer",
    request_body=customer_add_schema,
    responses={
        201: customer_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_customer(request, app_id):
    customer_object = request.data
    user = request.user
    app = request.app
    
    valid_params = check_params(customer_object, [
        {'param': 'customer_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])
    
    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = create_customer_record(customer_object, app, request.user)
            serializer = CustomerSerializer(result['customer'])
            return Response({'customer': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating customer: {e}')
            return Response({'errors': ['Failed to create customer.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_id="Add Customers",
    operation_description="Add a list of customers",
    request_body=customer_add_request_body,
    responses={
        200: add_customers_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def add_customers(request, app_id):
    data = request.data
    app = request.app

    customers_data = data.get('customers')
    if not isinstance(customers_data, list) or not customers_data:
        return Response({'errors': ['Customers list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(customers_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'customers_added': [], 'customers_not_added': []}

    try:
        with transaction.atomic():
            for index, customer_object in enumerate(customers_data):
                valid_params = check_params(customer_object, [
                    {'param': 'customer_id', 'type': 'string', 'required': False, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': True, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    result = create_customer_record(customer_object, app, request.user)
                    serializer = CustomerSerializer(result['customer'])
                    response_data['customers_added'].append(serializer.data)
                else:
                    response_data['customers_not_added'].append({
                        'index': index,
                        'submitted_object': customer_object,
                        'errors': valid_params['errors']
                    })
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error adding customers: {e}')
        return Response({'errors': ['Failed to add customers.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Updating customers
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Customers'],
    operation_id="Update Customer",
    operation_description="Update a customer",
    request_body=customer_update_schema,
    responses={
        201: customer_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_customer
def update_customer(request, app_id, customer_id):
    customer_object = request.data
    user = request.user
    app = request.app
    customer = request.customer
    
    valid_params = check_params(customer_object, [
        {'param': 'customer_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])

    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = update_customer_record(app, customer, customer_object)
            serializer = CustomerSerializer(result['customer'])
            return Response({'customer': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating customer: {e}')
            return Response({'errors': ['Failed to update customer.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['Customers'],
    operation_id="Update Customers",
    operation_description="Update a list of customers",
    request_body=customer_update_request_body,
    responses={
        200: update_customers_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def update_customers(request, app_id):
    data = request.data
    app = request.app

    customers_data = data.get('customers')
    if not isinstance(customers_data, list) or not customers_data:
        return Response({'errors': ['Customers list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(customers_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'customers_updated': [], 'customers_not_updated': []}

    try:
        with transaction.atomic():
            for index, customer_object in enumerate(customers_data):
                valid_params = check_params(customer_object, [
                    {'param': 'customer_id', 'type': 'string', 'required': True, 'length': 32},
                    {'param': 'name', 'type': 'string', 'required': False, 'length': 250},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    customer_id = customer_object['customer_id']
                    try:
                        customer = Customer.objects.get(customer_id=customer_id, app=app, status="active")
                        result = update_customer_record(app, customer, customer_object)
                        serializer = CustomerSerializer(result['customer'])
                        response_data['customers_updated'].append(serializer.data)
                    except Customer.DoesNotExist:
                        response_data['customers_not_updated'].append({
                            'index': index,
                            'submitted_object': customer_object,
                            'errors': ['Customer not found']
                        })
                else:
                    response_data['customers_not_updated'].append({
                        'index': index,
                        'submitted_object': customer_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error updating customers: {e}')
        return Response({'errors': ['Failed to update customers.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#-----------------------------------------------------------------------------------------------------------------------------
# Archiving customers
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['Customers'],
    operation_id="Archive Customer",
    operation_description="Archive a customer",
    responses={
        201: customer_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
@validate_customer
def archive_customer(request, app_id, customer_id):
    app = request.app
    customer = request.customer

    try:
        with transaction.atomic():
            customer.status = "archived"
            customer.save()
        serializer = CustomerSerializer(customer)
        return Response({'customer': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving customer: {e}')
        return Response({'errors': ['Failed to archive customer.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Customers'],
    operation_id="Archive Customers",
    operation_description="Archive a list of customers",
    request_body=customer_archive_request_body,
    responses={
        200: archive_customers_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def archive_customers(request, app_id):
    data = request.data
    app = request.app

    customers_data = data.get('customers')
    if not isinstance(customers_data, list) or not customers_data:
        return Response({'errors': ['Customers list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(customers_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'customers_archived': [], 'customers_not_archived': []}

    try:
        with transaction.atomic():
            for index, customer_object in enumerate(customers_data):
                valid_params = check_params(customer_object, [
                    {'param': 'customer_id', 'type': 'string', 'required': True, 'length': 32},
                ])

                if valid_params['valid']:
                    customer_id = customer_object['customer_id']
                    try:
                        customer = Customer.objects.get(customer_id=customer_id, app=app, status="active")
                        customer.status = "archived"
                        customer.save()
                        serializer = CustomerSerializer(customer)
                        response_data['customers_archived'].append(serializer.data)
                    except Customer.DoesNotExist:
                        response_data['customers_not_archived'].append({
                            'index': index,
                            'submitted_object': customer_object,
                            'errors': ['Customer not found']
                        })
                else:
                    response_data['customers_not_archived'].append({
                        'index': index,
                        'submitted_object': customer_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving customers: {e}')
        return Response({'errors': ['Failed to archive customers.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    tags=['Customers'],
    operation_id="Destroy Customers",
    operation_description="Destroy and archive all customers",
    request_body=None,
    responses={
        200: destroy_customers_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
@validate_app_user
def destroy_customers(request, app_id):
    user = request.user 
    app = request.app
    
    # Fetching apps that the user has access to and are active
    customers = Customer.objects.filter(app=app, status='active')

    if not customers:
        return Response({'errors': ['No active customers.']}, status=status.HTTP_400_BAD_REQUEST)

    # Update the status of each app to 'archived'
    for customer in customers:
        customer.status = 'archived'

    try:
        with transaction.atomic():
            Customer.objects.bulk_update(customers, ['status'])
        serializer = CustomerSerializer(customers, many=True)
        return Response({'customers_archived': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error destroying customers: {e}')
        return Response({'errors': ['Failed to destroy customers.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Export customers
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    operation_id="Export Customers",
    operation_description="Export customer data to a flat file",
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
def export_customers(request, app_id):
    user = request.user
    app = request.app

    # Get data elements for search, filters, date ranges, etc here

    # Query the data needed here

    # Initiate the background task for exporting

    return Response({'message': 'Export initiated'}, status=status.HTTP_202_ACCEPTED)


#-----------------------------------------------------------------------------------------------------------------------------
# Utils customers
#-----------------------------------------------------------------------------------------------------------------------------

def create_customer_record(data,  app, user):
    try:
        customer_id = data.get('customer_id', randomstr())

        customer_data = {
            'customer_id': customer_id,
            'name': data['name'],
            'app': app,
            'created_user': user,
            'data': data.get('data'),
            'config': data.get('config'),
        }

        # Remove None values from dictionary
        customer_data = {k: v for k, v in customer_data.items() if v is not None}

        customer = Customer.objects.create(**customer_data)

        return {
            'success': True,
            'customer': customer,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error creating the customer record'],
        }


def update_customer_record(app, customer, data):
    try:
        updated_fields = []

        for field in ['name', 'data', 'config']:
            if field in data:
                setattr(customer, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            customer.save(update_fields=updated_fields)

        return {
            'success': True,
            'customer': customer,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error updating the customer record'],
        }