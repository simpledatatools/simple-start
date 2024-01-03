from drf_yasg import openapi
from api.documentation.common_elements import date_time_properties


# Base Customer Schema
def base_customer_schema(required_fields=[], include_fields=None):
    all_properties = {
        'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        # Add other fields here
    }
    properties = {k: v for k, v in all_properties.items() if include_fields is None or k in include_fields}
    
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties,
        required=required_fields
    )

# Function to create a request body schema
def create_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=base_schema,
        description=description
    )

# Customer list response object
customer_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customers': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_customer_schema(), description='List of customers'),
        'page': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current page number'),
        'pages': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of pages'),
        'records_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of records')
    },
    description='Customer list response object with pages and record count'
)

# Customer response object
customer_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer': base_customer_schema()
    },
    description='Customer object'
)

# Adding response object
customer_not_added_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_customer_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a customer that could not be added'
)
add_customers_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customers_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_customer_schema(), description='List of successfully added customers'),
        'customers_not_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=customer_not_added_entry_schema, description='Details of customers that could not be added')
    },
    description='Response for the add customers operation'
)

# Updating response object
customer_not_updated_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_customer_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a customer that could not be updated'
)
update_customers_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customers_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_customer_schema(), description='List of successfully updated customers'),
        'customers_not_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=customer_not_updated_entry_schema, description='Details of customers that could not be updated')
    },
    description='Response for the add customers operation'
)

# Archiving response object
customer_not_archived_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_customer_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a customer that could not be archived'
)
archive_customers_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customers_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_customer_schema(), description='List of successfully archived customers'),
        'customers_not_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=customer_not_archived_entry_schema, description='Details of customers that could not be archived')
    },
    description='Response for the add customers operation'
)
destroy_customers_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customers_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_customer_schema(), description='List of successfully archived customers'),
    },
    description='Response for the add customers operation'
)

# Generate schemas for add and update operations
customer_add_schema = base_customer_schema(required_fields=['name'])
customer_update_schema = base_customer_schema(required_fields=['customer_id'])
customer_archive_schema = base_customer_schema(required_fields=['customer_id'], include_fields=['customer_id'])

# Function to create a request body schema that includes 'customers' key
def create_customers_key_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'customers': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_schema, description=description)
        },
        required=['customers']
    )

# Generate request body schemas with 'customers' key
customer_add_request_body = create_customers_key_request_body_schema(customer_add_schema, "List of customers to add")
customer_update_request_body = create_customers_key_request_body_schema(customer_update_schema, "List of customers to update")
customer_archive_request_body = create_customers_key_request_body_schema(customer_archive_schema, "List of customers to archive")

# Customer response schema
customer_schema = base_customer_schema()