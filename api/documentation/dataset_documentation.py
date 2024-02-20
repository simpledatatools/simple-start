from drf_yasg import openapi
from api.documentation.common_elements import date_time_properties


# Base Dataset Schema
def base_dataset_schema(required_fields=[], include_fields=None):
    all_properties = {
        'dataset_id': openapi.Schema(type=openapi.TYPE_STRING),
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

# Dataset list response object
dataset_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'datasets': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_dataset_schema(), description='List of datasets'),
        'page': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current page number'),
        'pages': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of pages'),
        'records_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of records')
    },
    description='Dataset list response object with pages and record count'
)

# Dataset response object
dataset_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'dataset': base_dataset_schema()
    },
    description='Dataset object'
)

# Adding response object
dataset_not_added_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_dataset_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a dataset that could not be added'
)
add_datasets_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'datasets_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_dataset_schema(), description='List of successfully added datasets'),
        'datasets_not_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=dataset_not_added_entry_schema, description='Details of datasets that could not be added')
    },
    description='Response for the add datasets operation'
)

# Updating response object
dataset_not_updated_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_dataset_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a dataset that could not be updated'
)
update_datasets_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'datasets_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_dataset_schema(), description='List of successfully updated datasets'),
        'datasets_not_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=dataset_not_updated_entry_schema, description='Details of datasets that could not be updated')
    },
    description='Response for the add datasets operation'
)

# Archiving response object
dataset_not_archived_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_dataset_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a dataset that could not be archived'
)
archive_datasets_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'datasets_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_dataset_schema(), description='List of successfully archived datasets'),
        'datasets_not_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=dataset_not_archived_entry_schema, description='Details of datasets that could not be archived')
    },
    description='Response for the add datasets operation'
)
destroy_datasets_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'datasets_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_dataset_schema(), description='List of successfully archived datasets'),
    },
    description='Response for the add datasets operation'
)

# Generate schemas for add and update operations
dataset_add_schema = base_dataset_schema(required_fields=['name'])
dataset_update_schema = base_dataset_schema(required_fields=['dataset_id'])
dataset_archive_schema = base_dataset_schema(required_fields=['dataset_id'], include_fields=['dataset_id'])

# Function to create a request body schema that includes 'datasets' key
def create_datasets_key_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'datasets': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_schema, description=description)
        },
        required=['datasets']
    )

# Generate request body schemas with 'datasets' key
dataset_add_request_body = create_datasets_key_request_body_schema(dataset_add_schema, "List of datasets to add")
dataset_update_request_body = create_datasets_key_request_body_schema(dataset_update_schema, "List of datasets to update")
dataset_archive_request_body = create_datasets_key_request_body_schema(dataset_archive_schema, "List of datasets to archive")

# Dataset response schema
dataset_schema = base_dataset_schema()