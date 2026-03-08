from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Owner, Project, SuperAdmin

User = get_user_model()


def get_display_name(user):
    """Return non-blank name: name, or first_name + last_name, or username."""
    if user.name and user.name.strip():
        return user.name.strip()
    parts = [user.first_name or '', user.last_name or '']
    combined = ' '.join(parts).strip()
    if combined:
        return combined
    return user.username or ''


def _normalize_choice(value, valid_choices):
    """Accept display or key; return lowercase key. valid_choices = [('key', 'Label'), ...]"""
    if value is None or value == '':
        return value
    s = str(value).strip().lower()
    for key, label in valid_choices:
        if key.lower() == s or (label and str(label).lower() == s):
            return key
    return value  # let default validation message apply


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - name always has a proper value (never blank). Saves all data on update. Role/status not required on update."""
    user_id = serializers.IntegerField(source='id', read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=User.STATUS_CHOICES, required=False)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'name', 'email', 'role', 'status',
            'created_date', 'is_active', 'date_joined'
        ]
        read_only_fields = ['user_id', 'username', 'created_date', 'date_joined']


class UserLoginResponseSerializer(serializers.ModelSerializer):
    """All stored user data for login API response (no password)."""
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'name', 'email', 'first_name', 'last_name',
            'role', 'status', 'created_date', 'created_at', 'updated_at',
            'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = get_display_name(instance)
        if data.get('last_login') is None:
            data['last_login'] = None
        return data

    def to_internal_value(self, data):
        # Normalize status/role so "Inactive" or "inactive" both work
        if isinstance(data, dict):
            data = data.copy()
            if 'status' in data and data['status']:
                data['status'] = _normalize_choice(data['status'], User.STATUS_CHOICES)
            if 'role' in data and data['role']:
                data['role'] = _normalize_choice(data['role'], User.ROLE_CHOICES)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure name is never blank: use name, or first_name+last_name, or username
        data['name'] = get_display_name(instance)
        return data

    def update(self, instance, validated_data):
        # Save all editable fields so GET returns correct data after edit
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(validated_data.keys()))
        instance.refresh_from_db()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users - only name (no first_name/last_name)."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'name', 'role', 'status']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating only user role."""
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)


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


class SuperAdminSerializer(serializers.ModelSerializer):
    """Serializer for SuperAdmin - no password in response."""
    class Meta:
        model = SuperAdmin
        fields = ['user_id', 'name', 'email', 'role', 'status']
        read_only_fields = ['user_id']


class SuperAdminCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SuperAdmin - password is write-only and hashed."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = SuperAdmin
        fields = ['name', 'email', 'password', 'role', 'status']

    def create(self, validated_data):
        password = validated_data.pop('password')
        obj = SuperAdmin(**validated_data)
        obj.set_password(password)
        obj.save()
        return obj


class SuperAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating SuperAdmin - password optional."""
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    class Meta:
        model = SuperAdmin
        fields = ['name', 'email', 'password', 'role', 'status']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer for login request (username + password)."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
