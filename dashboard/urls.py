from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='login.html'), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path("import/", views.import_observations, name="import_observations"),
    path('view-observations/', views.view_observations, name='view_observations'),
    path('update_observation/<int:pk>/', views.update_observation, name='update_observation'),
    path('upload_files/<int:observation_id>/', views.upload_files, name='upload_files'),
    path('download_file/<int:file_id>/', views.download_observation_file, name='download_observation_file'),

    path('upload-annexure/<int:observation_id>/', views.upload_annexure_files, name='upload_annexure_files'),
    path('download-annexure/<int:file_id>/', views.download_annexure_file, name='download_annexure_file'),


    path('delete_observation/<int:pk>/', views.delete_observation, name="delete_observation"),


    path('add_user/', views.add_user, name='add_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-password/', views.change_password, name='change_password'),
    

    path("departments/", views.manage_departments, name="manage_departments"),
    path("delete-department/<int:dept_id>/", views.delete_department, name="delete_department"),
    path("upload-departments/", views.upload_departments, name="upload_departments"),


    path("banks/", views.manage_banks, name="manage_banks"),
    path("delete-bank/<int:bank_id>/", views.delete_bank, name="delete_bank"),
    path("upload-banks/", views.upload_banks, name="upload_banks"),

    path('rbi-notifications/', views.rbi_notifications, name='rbi_notifications'),



]
