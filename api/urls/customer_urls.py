from django.urls import path
from api.views import customer_views as views

urlpatterns = [

    path('', views.get_customers, name="api_customers"),
    path('add/', views.add_customer, name="api_add_customer"),
    path('add/bulk/', views.add_customers, name="api_add_customers"),
    path('update/bulk/', views.update_customers, name="api_update_customers"),
    path('archive/bulk/', views.archive_customers, name="api_archive_customers"),
    path('destroy/', views.destroy_customers, name="api_destroy_customers"),
    path('export/', views.export_customers, name="api_export_customers"),
    path('<str:customer_id>/', views.get_customer, name="api_customer"),
    path('<str:customer_id>/update/', views.update_customer, name="api_update_customer"),
    path('<str:customer_id>/archive/', views.archive_customer, name="api_archive_customer"),
    
]