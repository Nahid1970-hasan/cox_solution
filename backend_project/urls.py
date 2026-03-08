"""
URL configuration for backend_project project.
"""
from django.contrib import admin
from django.urls import path, include

from .views import api_root, root_redirect, health
from users.views import (
    UserListCreateView,
    UserDetailView,
    UserRoleUpdateView,
    SuperAdminDashboardView,
    SuperAdminCreateView,
    SuperAdminDetailView,
)

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/health/', health),
    # User APIs
    path('api/dashboarduser/', UserListCreateView.as_view(), name='dashboarduser'), 
    path('api/alluser/', UserListCreateView.as_view(), name='alluser'),
    path('api/alluser/<int:pk>/', UserDetailView.as_view(), name='alluser-detail'),  # GET one user (edit modal), PUT/PATCH update
    path('api/addusers/', UserListCreateView.as_view(), name='adduser'),
    path('api/updateusers/<int:pk>/', UserDetailView.as_view(), name='update-user'),
    path('api/updateusers/<int:pk>/role/', UserRoleUpdateView.as_view(), name='user-update-role'),
    path('api/deleteusers/<int:pk>/', UserDetailView.as_view(), name='deleteuser'),
    # SuperAdmin (admin user) APIs
    path('api/superadmin_dashboard/', SuperAdminDashboardView.as_view(), name='superadmin-dashboard'),
    path('api/alladminuser/<int:pk>/', SuperAdminDetailView.as_view(), name='alladminuser-detail'),
    path('api/add_admin_users/', SuperAdminCreateView.as_view(), name='add-admin-users'),
    path('api/update_admin_users/<int:pk>/', SuperAdminDetailView.as_view(), name='update-admin-users'),
    path('api/delete_admin_users/<int:pk>/', SuperAdminDetailView.as_view(), name='delete-admin-users'),
    path('api/users/', include('users.urls')),
]
