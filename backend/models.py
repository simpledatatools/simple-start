from django.db import models
from django.db.models import JSONField
import uuid

from django.conf import settings
from files.models import *
from accounts.models import *
from core.utils import *

import datetime

from rest_framework_api_key.models import AbstractAPIKey


#-------------------------------------------------------------------------------
# App
#-------------------------------------------------------------------------------

class App(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(editable=False, max_length=32, null=True)
    name = models.CharField(max_length=250)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    status = models.CharField(
        max_length=25,
        choices=STATUS,
        blank=False,
        default='active',
    )
    
    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['app_id'], name='app_index'),
        ]


class AppUser(models.Model):
    id = models.AutoField(primary_key=True)
    app_user_id  = models.CharField(max_length=16, null=False, blank=True)
    app = models.ForeignKey('App', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name="app_user")
    email = models.CharField(max_length=250, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    ROLES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(
        max_length=25,
        choices=ROLES,
        blank=False,
        default='user',
    )

    STATUS = (
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('archived', 'Archived'),
    )
    
    status = models.CharField(
        max_length=25,
        choices=STATUS,
        blank=False,
        default='active',
    )

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['app_user_id'], name='app_user_index'),
        ]


class AppAPIKey(AbstractAPIKey):
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="app_api_keys",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta(AbstractAPIKey.Meta):
        verbose_name = "App API key"
        verbose_name_plural = "App API keys"


#-------------------------------------------------------------------------------
# Sample Model
#-------------------------------------------------------------------------------

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.CharField(editable=False, max_length=32, null=True)
    app = models.ForeignKey('App', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=250)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    status = models.CharField(
        max_length=25,
        choices=STATUS,
        blank=False,
        default='active',
    )
    
    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['customer_id'], name='customer_index'),
        ]


#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

class ImportTemplate(models.Model):

    id = models.AutoField(primary_key=True)
    template = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)

    LABEL = (
        ('tags-import-template', 'Tags Import Template'),
    )

    label = models.CharField(
        max_length=25,
        choices=LABEL,
        blank=False
    )


class ImportFile(models.Model):

    id = models.AutoField(primary_key=True)
    import_id = models.CharField(max_length=32, null=False, blank=True)
    import_file = models.ForeignKey('files.File', on_delete=models.SET_NULL, null=True)
    app = models.ForeignKey('App', on_delete=models.SET_NULL, null=True)
    rows = models.IntegerField(null=True, default=0)
    success_rows = models.IntegerField(null=True, default=0)
    failed_rows = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)

    import_type = models.CharField(max_length=25, null=True)

    IMPORT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    )

    status = models.CharField(
        max_length=25,
        choices=IMPORT_STATUS,
        blank=False,
        default='pending',
    )


class ImportFileLog(models.Model):

    id = models.AutoField(primary_key=True)
    log_id = models.CharField(max_length=32, null=False, blank=True)
    import_file = models.ForeignKey('ImportFile', on_delete=models.SET_NULL, null=True)
    row_number = models.IntegerField()
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    ROW_STATUS = (
        ('success', 'Success'),
        ('error', 'Error'),
    )

    row_status = models.CharField(
        max_length=25,
        choices=ROW_STATUS,
        blank=False
    )


#-------------------------------------------------------------------------------
# Exports
#-------------------------------------------------------------------------------

class ExportFile(models.Model):

    id = models.AutoField(primary_key=True)
    export_id = models.CharField(max_length=32, null=False, blank=True)
    export_file = models.FileField(upload_to='exports/', null=True)
    app = models.ForeignKey('App', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    
    export_type = models.CharField(max_length=25, null=True)

    EXPORT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    )

    status = models.CharField(
        max_length=25,
        choices=EXPORT_STATUS,
        blank=False,
        default='pending',
    )


#-------------------------------------------------------------------------------
# User Log
#-------------------------------------------------------------------------------

class UserLog(models.Model):
    id = models.AutoField(primary_key=True)
    user_log_id = models.CharField(editable=False, max_length=32, null=True)
    valid = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    view_name = models.CharField(editable=False, max_length=128, null=True)
    http_request_type = models.CharField(editable=False, max_length=16, null=True)
    ip_address = models.CharField(editable=False, max_length=64, null=True)
    path = models.CharField(editable=False, max_length=1000, null=True)
    full_path = models.CharField(editable=False, max_length=1000, null=True)
    data = models.JSONField(null=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['user_log_id'], name='user_log_index'),
        ]
