from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model (optional extension of Django's AbstractUser)."""

    email = models.EmailField(unique=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


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
    """Project table: project_id (PK), project_name, date, project_details, project_link."""

    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    project_details = models.TextField(blank=True)
    project_link = models.URLField(max_length=500, blank=True)
    img_url = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'project'
        ordering = ['project_id']

    def __str__(self):
        return self.project_name


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
