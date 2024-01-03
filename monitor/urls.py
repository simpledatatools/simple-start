from django.urls import path
from monitor.views import home as home
from monitor.views import apps as apps
from monitor.views import app_users as app_users
from monitor.views import profiles as profiles

urlpatterns = [

    path('', home.home, name='home'),
    
    # Apps
    path('apps/', apps.apps, name='apps'),
    path('ajax/apps/list/', apps.ajax_get_apps, name='ajax_get_apps'),
    path('ajax/apps/item/', apps.ajax_get_app_item, name='ajax_get_app_item'),
    path('apps/add/', apps.add_app, name='add_app'),
    path('ajax/apps/add/', apps.ajax_add_app, name='ajax_add_app'),
    path('apps/<app_id>/update/', apps.update_app, name='update_app'),
    path('ajax/apps/update/', apps.ajax_update_app, name='ajax_update_app'),
    path('ajax/apps/update/photo/', apps.ajax_update_app_photo, name='ajax_update_app_photo'),
    path('ajax/apps/update/photo/remove/', apps.ajax_remove_app_photo, name='ajax_remove_app_photo'),
    path('apps/<app_id>/remove/', apps.remove_app, name='remove_app'),
    path('ajax/apps/remove/', apps.ajax_remove_app, name='ajax_remove_app'),
    path('apps/<app_id>/details/', apps.app_details, name='app_details'),
    path('apps/<app_id>/setup/', apps.app_setup, name='app_setup'),
    path('apps/<app_id>/home/', apps.app_home, name='app_home'),
    path('apps/<app_id>/', apps.app, name='app'),

    # App Users
    path('apps/<app_id>/users/', app_users.app_users, name='app_users'),
    path('ajax/apps/<app_id>/users/list/', app_users.ajax_get_app_users, name='ajax_get_app_users'),
    path('ajax/apps/<app_id>/users/item/', app_users.ajax_get_app_user_item, name='ajax_get_app_user_item'),
    path('apps/<app_id>/users/add/', app_users.add_app_user, name='add_app_user'),
    path('ajax/apps/<app_id>/users/add/', app_users.ajax_add_app_user, name='ajax_add_app_user'),
    path('apps/<app_id>/users/<app_user_id>/update/', app_users.update_app_user, name='update_app_user'),
    path('ajax/apps/<app_id>/users/update/', app_users.ajax_update_app_user, name='ajax_update_app_user'),
    path('apps/<app_id>/users/<app_user_id>/remove/', app_users.remove_app_user, name='remove_app_user'),
    path('ajax/apps/<app_id>/users/remove/', app_users.ajax_remove_app_user, name='ajax_remove_app_user'),
    path('apps/<app_id>/users/<app_user_id>/details/', app_users.app_user_details, name='app_user_details'),

    # Profiles
    path('apps/<app_id>/profiles/', profiles.profiles, name='profiles'),
    path('ajax/apps/<app_id>/profiles/list/', profiles.ajax_get_profiles, name='ajax_get_profiles'),
    path('ajax/apps/<app_id>/profiles/item/', profiles.ajax_get_profile_item, name='ajax_get_profile_item'),
    path('apps/<app_id>/profiles/add/', profiles.add_profile, name='add_profile'),
    path('ajax/apps/<app_id>/profiles/add/', profiles.ajax_add_profile, name='ajax_add_profile'),
    path('apps/<app_id>/profiles/<profile_id>/update/', profiles.update_profile, name='update_profile'),
    path('ajax/apps/<app_id>/profiles/update/', profiles.ajax_update_profile, name='ajax_update_profile'),
    path('apps/<app_id>/profiles/<profile_id>/remove/', profiles.remove_profile, name='remove_profile'),
    path('ajax/apps/<app_id>/profiles/remove/', profiles.ajax_remove_profile, name='ajax_remove_profile'),
    path('apps/<app_id>/profiles/<profile_id>/details/', profiles.profile_details, name='profile_details'),

]