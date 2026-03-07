from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Owner, Project, LoginLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['owner_id', 'owner_name', 'owner_designation', 'email', 'img_url']
    search_fields = ['owner_name', 'email', 'owner_designation']
    ordering = ['owner_id']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'project_name', 'date', 'project_link', 'img_url']
    search_fields = ['project_name', 'project_details']
    ordering = ['project_id']


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    ordering = ['-created_at']
