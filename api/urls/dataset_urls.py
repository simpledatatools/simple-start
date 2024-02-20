from django.urls import path
from api.views import dataset_views as views

urlpatterns = [

    path('', views.get_datasets, name="api_datasets"),
    path('add/', views.add_dataset, name="api_add_dataset"),
    path('add/bulk/', views.add_datasets, name="api_add_datasets"),
    path('update/bulk/', views.update_datasets, name="api_update_datasets"),
    path('archive/bulk/', views.archive_datasets, name="api_archive_datasets"),
    path('destroy/', views.destroy_datasets, name="api_destroy_datasets"),
    path('export/', views.export_datasets, name="api_export_datasets"),
    path('<str:dataset_id>/', views.get_dataset, name="api_dataset"),
    path('<str:dataset_id>/update/', views.update_dataset, name="api_update_dataset"),
    path('<str:dataset_id>/archive/', views.archive_dataset, name="api_archive_dataset"),
    
]