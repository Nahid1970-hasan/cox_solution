from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Owner, Project, Blog, SuperAdmin, UploadFile, Contact, BillingInvoice, CompanyInfo

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
    """Accept display or key; return key. Handles 'Inactive', \"Inactive\", etc."""
    if value is None or value == '':
        return value
    # Strip quotes and whitespace (e.g. "\"Inactive\"" or " Inactive ")
    s = str(value).strip().strip('"\'').strip().lower()
    for key, label in valid_choices:
        if key.lower() == s or (label and str(label).strip().lower() == s):
            return key
    return value


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

    def to_internal_value(self, data):
        # Normalize status/role so "Inactive", "inactive", "\"Inactive\"" all work
        if isinstance(data, dict):
            data = data.copy()
            if 'status' in data and data['status'] is not None and str(data['status']).strip():
                data['status'] = _normalize_choice(data['status'], User.STATUS_CHOICES)
            if 'role' in data and data['role'] is not None and str(data['role']).strip():
                data['role'] = _normalize_choice(data['role'], User.ROLE_CHOICES)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = get_display_name(instance)
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(validated_data.keys()))
        instance.refresh_from_db()
        return instance


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
        fields = ['project_id', 'project_name', 'date', 'project_details', 'project_link', 'img_url', 'image_file', 'status']
        read_only_fields = ['project_id']

    def create(self, validated_data):
        """
        Support two flows:
        - Direct file upload via image_file (img_url derived from file URL)
        - Pre‑uploaded image where frontend sends img_url only (from /api/upload/)
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        project = super().create(validated_data)

        if image_file is not None:
            project.image_file = image_file
            project.img_url = project.image_file.url
        elif img_url:
            project.img_url = img_url

        project.save()
        return project

    def update(self, instance, validated_data):
        """
        Same dual support on update:
        - If image_file provided, overwrite image and img_url from file URL
        - Else if img_url provided, just update the URL string
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file is not None:
            instance.image_file = image_file
            instance.img_url = instance.image_file.url
        elif img_url is not None:
            instance.img_url = img_url

        instance.save()
        return instance


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog model (with optional image upload)."""

    class Meta:
        model = Blog
        fields = ['blog_id', 'blog_title', 'date', 'blog_content', 'blog_link', 'img_url', 'image_file', 'status']
        read_only_fields = ['blog_id']

    def create(self, validated_data):
        """
        Support two flows:
        - Direct file upload via image_file (img_url derived from file URL)
        - Pre‑uploaded image where frontend sends img_url only (from /api/upload/)
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        blog = super().create(validated_data)

        if image_file is not None:
            blog.image_file = image_file
            blog.img_url = blog.image_file.url
        elif img_url:
            blog.img_url = img_url

        blog.save()
        return blog

    def update(self, instance, validated_data):
        """
        Same dual support on update:
        - If image_file provided, overwrite image and img_url from file URL
        - Else if img_url provided, just update the URL string
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file is not None:
            instance.image_file = image_file
            instance.img_url = instance.image_file.url
        elif img_url is not None:
            instance.img_url = img_url

        instance.save()
        return instance


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact model (contact form submissions)."""

    class Meta:
        model = Contact
        fields = ['contact_id', 'name', 'email', 'message', 'date']
        read_only_fields = ['contact_id', 'date']


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


class UploadFileSerializer(serializers.ModelSerializer):
    """Serializer for uploaded files (image or any file)."""

    class Meta:
        model = UploadFile
        fields = ['id', 'file', 'original_name', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class BillingInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for BillingInvoice (get, add, update, delete).
    total_price is read-only: backend calculates it as subtotal - discount.
    own_com_name, own_com_title, own_com_logo always shown (from CompanyInfo if linked,
    else from invoice row). Accepts com_id and/or own_com_* (and camelCase) on write.
    """

    com_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    own_com_logo_file = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = BillingInvoice
        fields = [
            'invoice_id', 'invoice_no', 'com_id', 'own_com_name', 'own_com_title', 'own_com_logo', 'own_com_logo_file',
            'client_name', 'client_id', 'client_company', 'client_phone', 'client_address',
            'unit_price', 'total_price', 'billing_description', 'invoice_date',
            'subtotal', 'discount',
        ]
        read_only_fields = ['invoice_id', 'total_price']

    def to_internal_value(self, data):
        """Accept camelCase for company fields so frontend data is saved."""
        if isinstance(data, dict):
            data = data.copy()
            for camel, snake in [
                ('ownComName', 'own_com_name'),
                ('ownComTitle', 'own_com_title'),
                ('ownComLogo', 'own_com_logo'),
            ]:
                if camel in data and snake not in data:
                    data[snake] = data[camel]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('com_id', None)
        data.pop('own_com_logo_file', None)  # don't expose file field; use own_com_logo URL
        request = self.context.get('request')
        # Always return own_com_name, own_com_title, own_com_logo (from CompanyInfo or invoice; logo from URL or uploaded file)
        if instance.company_info_id and instance.company_info:
            data['own_com_name'] = (instance.company_info.own_com_name or '').strip() or ''
            data['own_com_title'] = (instance.company_info.own_com_title or '').strip() or ''
            data['own_com_logo'] = (instance.company_info.own_com_logo or '').strip() or ''
        else:
            data['own_com_name'] = (getattr(instance, 'own_com_name', None) or '').strip() or ''
            data['own_com_title'] = (getattr(instance, 'own_com_title', None) or '').strip() or ''
            logo_url = (getattr(instance, 'own_com_logo', None) or '').strip() or ''
            if not logo_url and getattr(instance, 'own_com_logo_file', None) and instance.own_com_logo_file:
                logo_url = instance.own_com_logo_file.url if not request else request.build_absolute_uri(instance.own_com_logo_file.url)
            data['own_com_logo'] = logo_url or ''
        return data

    def _apply_company_to_invoice(self, invoice, company_info):
        """Copy CompanyInfo (own_com_name, own_com_title, own_com_logo) into BillingInvoice row."""
        if company_info:
            invoice.own_com_name = (company_info.own_com_name or '').strip() or ''
            invoice.own_com_title = (company_info.own_com_title or '').strip() or ''
            invoice.own_com_logo = (company_info.own_com_logo or '').strip() or ''

    def create(self, validated_data):
        com_id = validated_data.pop('com_id', None)
        logo_file = validated_data.pop('own_com_logo_file', None)
        company_info = None
        if com_id is not None:
            try:
                company_info = CompanyInfo.objects.get(com_id=com_id)
            except CompanyInfo.DoesNotExist:
                pass
        invoice = BillingInvoice.objects.create(**validated_data)
        if logo_file:
            invoice.own_com_logo_file = logo_file
            request = self.context.get('request')
            invoice.own_com_logo = request.build_absolute_uri(invoice.own_com_logo_file.url) if request else invoice.own_com_logo_file.url
        if company_info:
            invoice.company_info = company_info
            self._apply_company_to_invoice(invoice, company_info)
        update_fields = ['own_com_name', 'own_com_title', 'own_com_logo']
        if company_info:
            update_fields = ['company_info'] + update_fields
        if logo_file:
            update_fields = ['own_com_logo_file'] + update_fields
        invoice.save(update_fields=update_fields)
        return invoice

    def update(self, instance, validated_data):
        com_id = validated_data.pop('com_id', None)
        logo_file = validated_data.pop('own_com_logo_file', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if logo_file is not None:
            instance.own_com_logo_file = logo_file
            request = self.context.get('request')
            instance.own_com_logo = request.build_absolute_uri(instance.own_com_logo_file.url) if request else instance.own_com_logo_file.url
        if com_id is not None:
            try:
                company_info = CompanyInfo.objects.get(com_id=com_id)
                instance.company_info = company_info
                self._apply_company_to_invoice(instance, company_info)
            except CompanyInfo.DoesNotExist:
                instance.company_info = None
        instance.save()
        return instance


class CompanyInfoSerializer(serializers.ModelSerializer):
    """Serializer for CompanyInfo (get, add, update, delete).
    Accepts both snake_case (own_com_name) and camelCase (ownComName) so frontend data is saved.
    """

    class Meta:
        model = CompanyInfo
        fields = ['com_id', 'own_com_name', 'own_com_title', 'own_com_logo']
        read_only_fields = ['com_id']

    def to_internal_value(self, data):
        """Accept camelCase from frontend and map to model fields."""
        if isinstance(data, dict):
            data = data.copy()
            for camel, snake in [
                ('ownComName', 'own_com_name'),
                ('ownComTitle', 'own_com_title'),
                ('ownComLogo', 'own_com_logo'),
            ]:
                if camel in data and snake not in data:
                    data[snake] = data[camel]
        return super().to_internal_value(data)
