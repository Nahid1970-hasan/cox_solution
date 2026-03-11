"""
URL configuration for backend_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import api_root, root_redirect, health, status_options
from users.views import (
    UserListCreateView,
    UserDetailView,
    UserRoleUpdateView,
    SuperAdminDashboardView,
    SuperAdminCreateView,
    SuperAdminDetailView,
    ProjectListCreateView,
    ProjectPublicDashboardView,
    ProjectDetailView,
    BlogListCreateView,
    BlogDetailView,
    UploadFileView,
    ContactListCreateView,
    ContactDetailView,
)

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/health/', health),
    path('api/status_options/', status_options),
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

    # Project APIs
    path('api/projectdashboard/', ProjectListCreateView.as_view(), name='project-dashboard'),
    path('api/projectall/<int:project_id>/', ProjectDetailView.as_view(), name='projectall-detail'),
    path('api/add_project/', ProjectListCreateView.as_view(), name='add-project'),
    path('api/update_project/<int:project_id>/', ProjectDetailView.as_view(), name='update-project'),
    path('api/delete_project/<int:project_id>/', ProjectDetailView.as_view(), name='delete-project'),
    path('api/project_public_dashboard/', ProjectPublicDashboardView.as_view(), name='project-public-dashboard'),

    # Blog APIs
    path('api/blogdashboard/', BlogListCreateView.as_view(), name='blog-dashboard'),
    path('api/blogall/<int:blog_id>/', BlogDetailView.as_view(), name='blogall-detail'),
    path('api/add_blog/', BlogListCreateView.as_view(), name='add-blog'),
    path('api/update_blog/<int:blog_id>/', BlogDetailView.as_view(), name='update-blog'),
    path('api/delete_blog/<int:blog_id>/', BlogDetailView.as_view(), name='delete-blog'),

    # Upload File APIs
    path('api/upload/', UploadFileView.as_view(), name='uploadfile'),

    # Contact APIs
    path('api/contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('api/save_contacts/', ContactListCreateView.as_view(), name='contact-save'),
    path('api/delete_contacts/<int:contact_id>/', ContactDetailView.as_view(), name='delete-contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
