from drf_yasg import openapi
from api.documentation.common_elements import date_time_properties


# Base Profile Schema
def base_profile_schema(required_fields=[], include_fields=None):
    all_properties = {
        'profile_id': openapi.Schema(type=openapi.TYPE_STRING),
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

# Profile list response object
profile_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profiles': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_profile_schema(), description='List of profiles'),
        'page': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current page number'),
        'pages': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of pages'),
        'records_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of records')
    },
    description='Profile list response object with pages and record count'
)

# Profile response object
profile_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profile': base_profile_schema()
    },
    description='Profile object'
)

# Adding response object
profile_not_added_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_profile_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a profile that could not be added'
)
add_profiles_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profiles_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_profile_schema(), description='List of successfully added profiles'),
        'profiles_not_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=profile_not_added_entry_schema, description='Details of profiles that could not be added')
    },
    description='Response for the add profiles operation'
)

# Updating response object
profile_not_updated_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_profile_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a profile that could not be updated'
)
update_profiles_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profiles_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_profile_schema(), description='List of successfully updated profiles'),
        'profiles_not_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=profile_not_updated_entry_schema, description='Details of profiles that could not be updated')
    },
    description='Response for the add profiles operation'
)

# Archiving response object
profile_not_archived_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_profile_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a profile that could not be archived'
)
archive_profiles_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profiles_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_profile_schema(), description='List of successfully archived profiles'),
        'profiles_not_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=profile_not_archived_entry_schema, description='Details of profiles that could not be archived')
    },
    description='Response for the add profiles operation'
)
destroy_profiles_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profiles_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_profile_schema(), description='List of successfully archived profiles'),
    },
    description='Response for the add profiles operation'
)

# Generate schemas for add and update operations
profile_add_schema = base_profile_schema(required_fields=['name'])
profile_update_schema = base_profile_schema(required_fields=['profile_id'])
profile_archive_schema = base_profile_schema(required_fields=['profile_id'], include_fields=['profile_id'])

# Function to create a request body schema that includes 'profiles' key
def create_profiles_key_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'profiles': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_schema, description=description)
        },
        required=['profiles']
    )

# Generate request body schemas with 'profiles' key
profile_add_request_body = create_profiles_key_request_body_schema(profile_add_schema, "List of profiles to add")
profile_update_request_body = create_profiles_key_request_body_schema(profile_update_schema, "List of profiles to update")
profile_archive_request_body = create_profiles_key_request_body_schema(profile_archive_schema, "List of profiles to archive")

# Profile response schema
profile_schema = base_profile_schema()