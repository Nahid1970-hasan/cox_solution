from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Owner, Project, Blog, LoginLog, SuperAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'name', 'email', 'role', 'status', 'created_date', 'date_joined']
    list_filter = ['role', 'status', 'is_staff', 'is_active']
    search_fields = ['username', 'name', 'email', 'first_name', 'last_name']
    ordering = ['-created_date', '-date_joined']


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


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['blog_id', 'blog_title', 'date', 'blog_link', 'img_url']
    search_fields = ['blog_title', 'blog_content']
    ordering = ['blog_id']


class SuperAdminAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)

    class Meta:
        model = SuperAdmin
        fields = ['name', 'email', 'password', 'role', 'status']

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.cleaned_data.get('password'):
            obj.set_password(self.cleaned_data['password'])
        if commit:
            obj.save()
        return obj


@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    form = SuperAdminAdminForm
    list_display = ['user_id', 'name', 'email', 'role', 'status']
    search_fields = ['name', 'email']
    ordering = ['user_id']


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    ordering = ['-created_at']
