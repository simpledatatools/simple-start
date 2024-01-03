from drf_yasg import openapi
from api.documentation.common_elements import date_time_properties


# Base Customer Schema
def base_app_schema(required_fields=[], include_fields=None):
    all_properties = {
        'app_id': openapi.Schema(type=openapi.TYPE_STRING),
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
app_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'apps': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_app_schema(), description='List of apps'),
        'page': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current page number'),
        'pages': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of pages'),
        'records_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of records')
    },
    description='Customer list response object with pages and record count'
)

# Customer response object
app_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'app': base_app_schema()
    },
    description='Customer object'
)

# Adding response object
app_not_added_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_app_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a app that could not be added'
)
add_apps_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'apps_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_app_schema(), description='List of successfully added apps'),
        'apps_not_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=app_not_added_entry_schema, description='Details of apps that could not be added')
    },
    description='Response for the add apps operation'
)

# Updating response object
app_not_updated_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_app_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a app that could not be updated'
)
update_apps_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'apps_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_app_schema(), description='List of successfully updated apps'),
        'apps_not_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=app_not_updated_entry_schema, description='Details of apps that could not be updated')
    },
    description='Response for the add apps operation'
)

# Archiving response object
app_not_archived_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_app_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a app that could not be archived'
)
archive_apps_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'apps_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_app_schema(), description='List of successfully archived apps'),
        'apps_not_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=app_not_archived_entry_schema, description='Details of apps that could not be archived')
    },
    description='Response for the add apps operation'
)
destroy_apps_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'apps_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_app_schema(), description='List of successfully archived apps'),
    },
    description='Response for the add apps operation'
)

# Generate schemas for add and update operations
app_add_schema = base_app_schema(required_fields=['name'])
app_update_schema = base_app_schema(required_fields=['app_id'])
app_archive_schema = base_app_schema(required_fields=['app_id'], include_fields=['app_id'])

# Function to create a request body schema that includes 'apps' key
def create_apps_key_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'apps': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_schema, description=description)
        },
        required=['apps']
    )

# Generate request body schemas with 'apps' key
app_add_request_body = create_apps_key_request_body_schema(app_add_schema, "List of apps to add")
app_update_request_body = create_apps_key_request_body_schema(app_update_schema, "List of apps to update")
app_archive_request_body = create_apps_key_request_body_schema(app_archive_schema, "List of apps to archive")

# Customer response schema
app_schema = base_app_schema()