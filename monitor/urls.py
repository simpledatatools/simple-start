from django.urls import path
from monitor.views import home as home
from monitor.views import apps as apps
from monitor.views import app_users as app_users
from monitor.views import customers as customers

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

    # Customers
    path('apps/<app_id>/customers/', customers.customers, name='customers'),
    path('ajax/apps/<app_id>/customers/list/', customers.ajax_get_customers, name='ajax_get_customers'),
    path('ajax/apps/<app_id>/customers/item/', customers.ajax_get_customer_item, name='ajax_get_customer_item'),
    path('apps/<app_id>/customers/add/', customers.add_customer, name='add_customer'),
    path('ajax/apps/<app_id>/customers/add/', customers.ajax_add_customer, name='ajax_add_customer'),
    path('apps/<app_id>/customers/<customer_id>/update/', customers.update_customer, name='update_customer'),
    path('ajax/apps/<app_id>/customers/update/', customers.ajax_update_customer, name='ajax_update_customer'),
    path('apps/<app_id>/customers/<customer_id>/remove/', customers.remove_customer, name='remove_customer'),
    path('ajax/apps/<app_id>/customers/remove/', customers.ajax_remove_customer, name='ajax_remove_customer'),
    path('apps/<app_id>/customers/<customer_id>/details/', customers.customer_details, name='customer_details'),

]