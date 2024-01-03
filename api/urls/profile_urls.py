from django.urls import path
from api.views import profile_views as views

urlpatterns = [

    path('', views.get_profiles, name="api_profiles"),
    path('add/', views.add_profile, name="api_add_profile"),
    path('add/bulk/', views.add_profiles, name="api_add_profiles"),
    path('update/bulk/', views.update_profiles, name="api_update_profiles"),
    path('archive/bulk/', views.archive_profiles, name="api_archive_profiles"),
    path('destroy/', views.destroy_profiles, name="api_destroy_profiles"),
    path('export/', views.export_profiles, name="api_export_profiles"),
    path('<str:profile_id>/', views.get_profile, name="api_profile"),
    path('<str:profile_id>/update/', views.update_profile, name="api_update_profile"),
    path('<str:profile_id>/archive/', views.archive_profile, name="api_archive_profile"),
    
]