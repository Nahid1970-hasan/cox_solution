from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Owner APIs
    path('owners/', views.OwnerListCreateView.as_view(), name='owner-list-create'),
    path('owners/<int:owner_id>/', views.OwnerDetailView.as_view(), name='owner-detail'),
    # Project APIs
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    # Contact APIs
    path('contacts/', views.ContactListCreateView.as_view(), name='contact-list-create'),
    # Login / Logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
