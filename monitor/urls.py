from django.urls import path
from monitor.views import home as home
from monitor.views import apps as apps
from monitor.views import app_users as app_users
from monitor.views import datasets as datasets

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

    # Datasets
    path('apps/<app_id>/datasets/', datasets.datasets, name='datasets'),
    path('ajax/apps/<app_id>/datasets/list/', datasets.ajax_get_datasets, name='ajax_get_datasets'),
    path('ajax/apps/<app_id>/datasets/item/', datasets.ajax_get_dataset_item, name='ajax_get_dataset_item'),
    path('apps/<app_id>/datasets/add/', datasets.add_dataset, name='add_dataset'),
    path('ajax/apps/<app_id>/datasets/add/', datasets.ajax_add_dataset, name='ajax_add_dataset'),
    path('apps/<app_id>/datasets/<dataset_id>/update/', datasets.update_dataset, name='update_dataset'),
    path('ajax/apps/<app_id>/datasets/update/', datasets.ajax_update_dataset, name='ajax_update_dataset'),
    path('apps/<app_id>/datasets/<dataset_id>/remove/', datasets.remove_dataset, name='remove_dataset'),
    path('ajax/apps/<app_id>/datasets/remove/', datasets.ajax_remove_dataset, name='ajax_remove_dataset'),
    path('apps/<app_id>/datasets/<dataset_id>/details/', datasets.dataset_details, name='dataset_details'),

]