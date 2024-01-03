from django.urls import path
from api.views import app_views as views

urlpatterns = [

    path('', views.get_apps, name="api_apps"),
    path('add/', views.add_app, name="api_add_app"),
    path('add/bulk/', views.add_apps, name="api_add_apps"),
    path('update/bulk/', views.update_apps, name="api_update_apps"),
    path('archive/bulk/', views.archive_apps, name="api_archive_apps"),
    path('destroy/', views.destroy_apps, name="api_destroy_apps"),
    path('export/', views.export_apps, name="api_export_apps"),
    path('<str:app_id>/', views.get_app, name="api_app"),
    path('<str:app_id>/update/', views.update_app, name="api_update_app"),
    path('<str:app_id>/archive/', views.archive_app, name="api_archive_app"),
    
]