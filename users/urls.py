from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    # Owner APIs
    path('owners/', views.OwnerListCreateView.as_view(), name='owner-list-create'),
    path('owners/<int:owner_id>/', views.OwnerDetailView.as_view(), name='owner-detail'),
    # Project APIs
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    # Login / Logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
