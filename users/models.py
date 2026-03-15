from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models


class User(AbstractUser):
    """User table: users who can login. user_id (id), name, email, role, status, created_date."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('superadmin', 'Superadmin'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    email = models.EmailField(unique=True, blank=False)
    name = models.CharField(max_length=255, blank=True)  # Name
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user'
        ordering = ['-created_date', '-date_joined']

    def __str__(self):
        return self.name or self.username


class Owner(models.Model):
    """Owner table: owner_id (PK), owner_name, owner_designation, email, owner_details."""

    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=255)
    owner_designation = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    owner_details = models.TextField(blank=True)
    img_url = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'owner'
        ordering = ['owner_id']

    def __str__(self):
        return self.owner_name


class Project(models.Model):
    """Project table: project_id (PK), project_name, date, project_details, project_link, status."""

    STATUS_CHOICES = [
        ('incoming', 'Incoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    project_details = models.TextField(blank=True)
    project_link = models.URLField(max_length=500, blank=True)
    img_url = models.URLField(max_length=500, blank=True)
    image_file = models.FileField(upload_to='project_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incoming', blank=True)

    class Meta:
        db_table = 'project'
        ordering = ['project_id']

    def __str__(self):
        return self.project_name

class Blog(models.Model):
    """Blog table: blog_id (PK), blog_title, date, blog_content, blog_link, status."""

    STATUS_CHOICES = [
        ('incoming', 'Incoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    blog_id = models.AutoField(primary_key=True)
    blog_title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    blog_content = models.TextField(blank=True)
    blog_link = models.URLField(max_length=500, blank=True)
    img_url = models.URLField(max_length=500, blank=True)
    image_file = models.FileField(upload_to='blog_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incoming', blank=True)

    class Meta:
        db_table = 'blog'
        ordering = ['blog_id']

    def __str__(self):
        return self.blog_title

class SuperAdmin(models.Model):
    """Superadmin table: user_id (PK), name, email, password, role, status."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # stored hashed
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='superadmin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'superadmin'
        ordering = ['user_id']

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class UploadFile(models.Model):
    """Uploaded files (images or other files) stored for the API."""

    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'upload_file'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name or self.file.name


class LoginLog(models.Model):
    """Table to record login and logout events."""

    LOGIN = 'login'
    LOGOUT = 'logout'
    ACTION_CHOICES = [(LOGIN, 'Login'), (LOGOUT, 'Logout')]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.created_at}"


class Contact(models.Model):
    """Contact table: contact_id (PK), name, email, message, date."""

    contact_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'contact'
        ordering = ['-date', 'contact_id']

    def __str__(self):
        return f"{self.name} <{self.email}>"


class BillingInvoice(models.Model):
    """Billing invoice table: invoice_id (PK), company/client details, pricing, dates.
    Company block: company_info (FK to CompanyInfo) plus own_com_name, own_com_title, own_com_logo
    stored on this table. When company_info is set, name/title/logo are synced from CompanyInfo
    into these fields so the invoice row always has them; API returns from CompanyInfo when linked.
    """

    invoice_id = models.AutoField(primary_key=True)
    invoice_no = models.CharField(max_length=100, blank=True)  # e.g. INV-2025-001
    company_info = models.ForeignKey(
        'users.CompanyInfo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
    )
    # From CompanyInfo when com_id is set, or set directly (e.g. "COX WEB SOLUTIONS", "INnovate, Integrate, Elevate")
    own_com_name = models.CharField(max_length=255, blank=True)
    own_com_title = models.CharField(max_length=255, blank=True)
    own_com_logo = models.URLField(max_length=500, blank=True)  # URL from web or set from uploaded file
    own_com_logo_file = models.ImageField(upload_to='invoice_logos/', blank=True, null=True)  # logo from folder/file upload
    client_name = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=100, blank=True)
    client_company = models.CharField(max_length=255, blank=True)
    client_phone = models.CharField(max_length=50, blank=True)
    client_address = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    billing_description = models.TextField(blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = 'billing_invoice'
        ordering = ['-invoice_date', '-invoice_id']

    def save(self, *args, **kwargs):
        """Calculate total_price from unit_price and discount: total_price = unit_price - discount (e.g. 123.00 - 10.00 = 113.00)."""
        unit = self.unit_price
        disc = self.discount
        if unit is None:
            unit = Decimal('0')
        else:
            unit = Decimal(str(unit))
        if disc is None:
            disc = Decimal('0')
        else:
            disc = Decimal(str(disc))
        total = unit - disc
        self.total_price = max(Decimal('0'), total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_id} - {self.client_name or 'N/A'}"


class CompanyInfo(models.Model):
    """Company info table: com_id (PK), own_com_name, own_com_title, own_com_logo.
    Used by BillingInvoice: when an invoice links here (company_info), these fields
    are copied into the invoice's own_com_name, own_com_title, own_com_logo.
    """

    com_id = models.AutoField(primary_key=True)
    own_com_name = models.CharField(max_length=255, blank=True)   # e.g. "COX WEB SOLUTIONS"
    own_com_title = models.CharField(max_length=255, blank=True)  # e.g. "INnovate, Integrate, Elevate"
    own_com_logo = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'companyinfo'
        ordering = ['com_id']

    def __str__(self):
        return self.own_com_name or f"Company #{self.com_id}"
