from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf.urls.static import static

from rest_framework import permissions

from django.conf.urls import handler403, handler404, handler500
from monitor.views import errors as errors

handler500 = errors.error_500
handler403 = errors.error_403
handler404 = errors.error_404

from .views import robots_txt

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="SimpleStart API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [

    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API: Users
    path('api/users/', include('api.urls.user_urls')),
    
    # API: Apps
    path('api/apps/', include('api.urls.app_urls')),

    # API: Customers
    path('api/apps/<str:app_id>/profiles/', include('api.urls.profile_urls')),
    
    # Web App
    path('internal/', admin.site.urls), # Standard django admin app
    path('', include('accounts.urls')),
    path('', include('monitor.urls')),
    path('files/', include('files.urls')),
    path("robots.txt", robots_txt),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Simple Start Admin Panel"
admin.site.site_title = "Simple Start Admin Panel"
admin.site.index_title = ""
