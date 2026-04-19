import datetime as dt

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import serializers

from .models import Owner, Project, Blog, SuperAdmin, UploadFile, Contact, BillingInvoice, CompanyInfo, Client, ClientPublic

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


def _normalize_blog_link(value):
    """Allow empty, absolute URLs, path-only links; add https:// for bare hostnames."""
    v = (value or '').strip()
    if not v:
        return ''
    lower = v.lower()
    if lower.startswith(('http://', 'https://', 'mailto:')):
        return v
    if v.startswith('/'):
        return v
    if v.startswith('//'):
        return 'https:' + v
    return f'https://{v}'


def _normalize_media_image_url(value):
    """Normalize common frontend image URL variants to valid MEDIA_URL paths."""
    v = (value or '').strip()
    if not v:
        return ''

    lowered = v.lower()
    if lowered.startswith(('http://', 'https://', 'data:')):
        return v

    normalized = v.replace('\\', '/')
    media_url = (settings.MEDIA_URL or '/media/').rstrip('/')

    # If frontend sends an absolute local path, keep only the filename.
    if ':/' in normalized and '/media/' in normalized.lower():
        normalized = normalized.split('/media/', 1)[1]
    if ':\\' in v:
        normalized = normalized.split('/')[-1]

    if normalized.startswith('/'):
        normalized = normalized.lstrip('/')
    if normalized.startswith('media/'):
        normalized = normalized[len('media/'):]

    if normalized.startswith('uploads/') or normalized.startswith('blog_images/') or normalized.startswith('project_images/'):
        return f"{media_url}/{normalized}"

    # Bare filename or unknown relative path: prefer uploads folder if file exists there.
    if '/' not in normalized:
        upload_candidate = f"uploads/{normalized}"
        if default_storage.exists(upload_candidate):
            return f"{media_url}/{upload_candidate}"

    # Keep under MEDIA_URL to avoid broken absolute filesystem paths.
    return f"{media_url}/{normalized}"


class FlexibleDateField(serializers.DateField):
    """Accept YYYY-MM-DD and ISO-8601 datetimes (e.g. from JavaScript Date.toISOString())."""

    def to_internal_value(self, value):
        if value in (None, ''):
            return None
        if isinstance(value, dt.datetime):
            return value.date()
        if isinstance(value, dt.date):
            return value
        s = str(value).strip()
        if not s:
            return None
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            try:
                return dt.date.fromisoformat(s[:10])
            except ValueError:
                pass
        s_adj = s.replace('Z', '+00:00')
        try:
            parsed = dt.datetime.fromisoformat(s_adj)
            return parsed.date()
        except ValueError:
            pass
        pd = parse_date(s)
        if pd:
            return pd
        pdt = parse_datetime(s_adj)
        if pdt:
            return pdt.date()
        raise serializers.ValidationError(
            'Date has wrong format. Use YYYY-MM-DD or an ISO-8601 datetime.'
        )


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
    """Serializer for User model - name always has a proper value (never blank). Username/email/name updatable; list and detail stay in sync."""
    user_id = serializers.IntegerField(source='id', read_only=True)
    username = serializers.CharField(required=False, allow_blank=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=User.STATUS_CHOICES, required=False)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'name', 'first_name', 'last_name', 'email', 'role', 'status',
            'created_date', 'is_active', 'date_joined'
        ]
        read_only_fields = ['user_id', 'created_date', 'date_joined']

    def validate_username(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError('Username cannot be empty.')
        value = str(value).strip()
        qs = User.objects.filter(username=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A user with this username already exists.')
        return value

    def validate_email(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            raise serializers.ValidationError('Email is required.')
        value = str(value).strip().lower()
        qs = User.objects.filter(email=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def to_internal_value(self, data):
        # Normalize status/role; map common frontend keys (camelCase) to model fields
        if isinstance(data, dict):
            data = data.copy()
            for alt, key in [
                ('userName', 'username'),
                ('user_name', 'username'),
                ('fullName', 'name'),
                ('full_name', 'name'),
                ('displayName', 'name'),
                ('display_name', 'name'),
                ('firstName', 'first_name'),
                ('lastName', 'last_name'),
                ('userStatus', 'status'),
                ('accountStatus', 'status'),
            ]:
                if alt in data and key not in data:
                    data[key] = data[alt]
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
        if 'status' in validated_data:
            instance.is_active = validated_data['status'] == 'active'
        # Full save so auto_now (updated_at) and auth-related side effects apply; avoid partial update_fields.
        instance.save()
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
    """Serializer for creating users. Status/role accept DB keys or labels ('Active' / 'Inactive')."""

    password = serializers.CharField(write_only=True, min_length=8)
    status = serializers.ChoiceField(choices=User.STATUS_CHOICES, required=False, default='active')
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False, default='user')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'name', 'role', 'status']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            for alt, key in [
                ('userName', 'username'),
                ('user_name', 'username'),
                ('fullName', 'name'),
                ('full_name', 'name'),
                ('userStatus', 'status'),
                ('accountStatus', 'status'),
            ]:
                if alt in data and key not in data:
                    data[key] = data[alt]
            if 'status' in data and data['status'] is not None and str(data['status']).strip():
                data['status'] = _normalize_choice(data['status'], User.STATUS_CHOICES)
            if 'role' in data and data['role'] is not None and str(data['role']).strip():
                data['role'] = _normalize_choice(data['role'], User.ROLE_CHOICES)
        return super().to_internal_value(data)

    def create(self, validated_data):
        status_val = validated_data.get('status', 'active')
        validated_data['is_active'] = status_val == 'active'
        user = User.objects.create_user(**validated_data)
        return user


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating only user role."""
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client (dashboard CRUD); saving updates client_public via model save."""

    date = FlexibleDateField(required=False, allow_null=True)

    class Meta:
        model = Client
        fields = [
            'client_id', 'client_name', 'email', 'phone_number', 'client_company_name',
            'address', 'date',
        ]
        read_only_fields = ['client_id']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            for camel, snake in [
                ('clientName', 'client_name'),
                ('phoneNumber', 'phone_number'),
                ('clientCompanyName', 'client_company_name'),
            ]:
                if camel in data and snake not in data:
                    data[snake] = data[camel]
        return super().to_internal_value(data)


class ClientPublicSerializer(serializers.ModelSerializer):
    """Read-only snapshot for public client dashboard (client_public table)."""

    client_id = serializers.IntegerField(source='client.client_id', read_only=True)

    class Meta:
        model = ClientPublic
        fields = [
            'client_id', 'client_name', 'email', 'phone_number', 'client_company_name',
            'address', 'date', 'synced_at',
        ]
        read_only_fields = [
            'client_name', 'email', 'phone_number', 'client_company_name',
            'address', 'date', 'synced_at',
        ]


class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for Owner model (get, insert, update)."""

    class Meta:
        model = Owner
        fields = ['owner_id', 'owner_name', 'owner_designation', 'email', 'owner_details', 'img_url']
        read_only_fields = ['owner_id']


def _empty_uploaded_file(f):
    """Multipart forms often send an empty file field; treat as no upload."""
    if f is None:
        return True
    try:
        return getattr(f, 'size', 0) == 0
    except Exception:
        return False


def _delete_image_file_if_present(instance):
    """Remove previous upload from storage and clear the FileField (save=False)."""
    f = getattr(instance, 'image_file', None)
    if f and getattr(f, 'name', None):
        f.delete(save=False)


def _media_urls_equivalent(a, b):
    """True if two URL strings refer to the same path under MEDIA (host/path variants)."""
    a = (a or '').strip().replace('\\', '/')
    b = (b or '').strip().replace('\\', '/')
    if not a or not b:
        return a == b
    if a == b:
        return True

    def path_key(u):
        u = u.lower()
        if '/media/' in u:
            return u.split('/media/', 1)[-1].strip('/')
        u = u.lstrip('/')
        if u.startswith('media/'):
            return u[6:].strip('/')
        return u.strip('/')

    return path_key(a) == path_key(b)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model.
    img_url uses CharField (not URLField) so full media URLs and path-style values validate.
    image_file binary upload takes precedence; img_url is normalized to MEDIA paths.
    """

    img_url = serializers.CharField(max_length=500, allow_blank=True, required=False, allow_null=True)
    project_link = serializers.CharField(max_length=500, allow_blank=True, required=False, allow_null=True)
    date = FlexibleDateField(required=False, allow_null=True)

    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'date', 'project_details', 'project_link', 'img_url', 'image_file', 'status']
        read_only_fields = ['project_id']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            for camel, snake in [
                ('imgUrl', 'img_url'),
                ('imageFile', 'image_file'),
                ('projectName', 'project_name'),
                ('projectDetails', 'project_details'),
                ('projectLink', 'project_link'),
            ]:
                if camel in data and snake not in data:
                    data[snake] = data[camel]
            if 'status' in data and data['status'] is not None and str(data['status']).strip():
                data['status'] = _normalize_choice(data['status'], Project.STATUS_CHOICES)
        return super().to_internal_value(data)

    def validate_img_url(self, value):
        return _normalize_media_image_url(value or '')

    def validate_project_link(self, value):
        return _normalize_blog_link(value or '')

    def create(self, validated_data):
        """
        Support two flows:
        - Direct file upload via image_file (img_url derived from file URL)
        - Pre‑uploaded image where frontend sends img_url only (from /api/upload/)
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        if _empty_uploaded_file(image_file):
            image_file = None

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
        On new upload, previous image_file is deleted from storage.
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        if _empty_uploaded_file(image_file):
            image_file = None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file is not None:
            _delete_image_file_if_present(instance)
            instance.image_file = image_file
            instance.img_url = instance.image_file.url
        elif img_url is not None:
            if instance.image_file and instance.image_file.name:
                try:
                    current_url = instance.image_file.url
                except Exception:
                    current_url = ''
                if not _media_urls_equivalent(img_url, current_url):
                    _delete_image_file_if_present(instance)
            instance.img_url = img_url

        instance.save()
        return instance


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog model (with optional image upload)."""

    blog_link = serializers.CharField(
        max_length=500, allow_blank=True, allow_null=True, required=False
    )
    img_url = serializers.CharField(
        max_length=500, allow_blank=True, allow_null=True, required=False
    )
    blog_image_url = serializers.SerializerMethodField(read_only=True)
    date = FlexibleDateField(required=False, allow_null=True)

    class Meta:
        model = Blog
        fields = ['blog_id', 'blog_title', 'date', 'blog_content', 'blog_link', 'img_url', 'blog_image_url', 'image_file', 'status']
        read_only_fields = ['blog_id']

    def validate_blog_link(self, value):
        return _normalize_blog_link(value)

    def validate(self, attrs):
        # Model URLFields are non-null; JSON/multipart may send null for cleared fields.
        if attrs.get('img_url') is None:
            attrs['img_url'] = ''
        else:
            attrs['img_url'] = _normalize_media_image_url(attrs.get('img_url'))
        if attrs.get('blog_link') is None:
            attrs['blog_link'] = ''
        return attrs

    def create(self, validated_data):
        """
        Support two flows:
        - Direct file upload via image_file (img_url derived from file URL)
        - Pre‑uploaded image where frontend sends img_url only (from /api/upload/)
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        if _empty_uploaded_file(image_file):
            image_file = None

        blog = super().create(validated_data)

        if image_file is not None:
            blog.image_file = image_file
            blog.img_url = blog.image_file.url
        elif img_url:
            blog.img_url = _normalize_media_image_url(img_url)

        blog.save()
        return blog

    def update(self, instance, validated_data):
        """
        Same dual support on update:
        - If image_file provided, overwrite image and img_url from file URL
        - Else if img_url provided, just update the URL string
        On new upload, previous image_file is deleted from storage.
        """
        image_file = validated_data.pop('image_file', None)
        img_url = validated_data.pop('img_url', None)

        if _empty_uploaded_file(image_file):
            image_file = None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file is not None:
            _delete_image_file_if_present(instance)
            instance.image_file = image_file
            instance.img_url = instance.image_file.url
        elif img_url is not None:
            normalized = _normalize_media_image_url(img_url)
            if instance.image_file and instance.image_file.name:
                try:
                    current_url = instance.image_file.url
                except Exception:
                    current_url = ''
                if not _media_urls_equivalent(normalized, current_url):
                    _delete_image_file_if_present(instance)
            instance.img_url = normalized

        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        img_url = (data.get('img_url') or '').strip()
        if img_url:
            data['img_url'] = _normalize_media_image_url(img_url)
        elif getattr(instance, 'image_file', None):
            data['img_url'] = instance.image_file.url
        return data

    def get_blog_image_url(self, obj):
        request = self.context.get('request')
        relative = f"/api/blog_image/{obj.blog_id}/"
        return request.build_absolute_uri(relative) if request else relative


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
