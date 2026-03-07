from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Owner, Project

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for Owner model (get, insert, update)."""

    class Meta:
        model = Owner
        fields = ['owner_id', 'owner_name', 'owner_designation', 'email', 'owner_details', 'img_url']
        read_only_fields = ['owner_id']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""

    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'date', 'project_details', 'project_link', 'img_url']
        read_only_fields = ['project_id']


class LoginSerializer(serializers.Serializer):
    """Serializer for login request (username + password)."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
