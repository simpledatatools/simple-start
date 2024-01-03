from drf_yasg import openapi

date_time_properties = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'year': openapi.Schema(type=openapi.TYPE_INTEGER),
        'month': openapi.Schema(type=openapi.TYPE_INTEGER),
        'day': openapi.Schema(type=openapi.TYPE_INTEGER),
        'hour': openapi.Schema(type=openapi.TYPE_INTEGER),
        'minute': openapi.Schema(type=openapi.TYPE_INTEGER),
        'second': openapi.Schema(type=openapi.TYPE_INTEGER),
        'timezone': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'errors': openapi.Schema(
            type=openapi.TYPE_ARRAY, 
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description="List of error messages"
        ),
    }
)

success_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(
            type=openapi.TYPE_STRING
        ),
    }
)
