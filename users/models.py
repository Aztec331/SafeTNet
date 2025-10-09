from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'


class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('SUB_ADMIN', 'Sub Admin'),
        ('USER', 'User'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='USER'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class SubAdminProfile(models.Model):
    PERMISSION_CHOICES = [
        ('READ_ONLY', 'Read Only'),
        ('READ_WRITE', 'Read & Write'),
        ('FULL_ACCESS', 'Full Access'),
    ]
    
    SCOPE_CHOICES = [
        ('GLOBAL', 'Global'),
        ('REGIONAL', 'Regional'),
        ('LOCAL', 'Local'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='subadmin_profile',
        limit_choices_to={'role': 'SUB_ADMIN'}
    )
    permissions = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='READ_ONLY'
    )
    assigned_scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default='LOCAL'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_subadmins',
        limit_choices_to={'role': 'SUPER_ADMIN'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sub Admin Profile'
        verbose_name_plural = 'Sub Admin Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.permissions} ({self.assigned_scope})"


class Geofence(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    polygon_json = models.JSONField(help_text="GeoJSON polygon coordinates")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='geofences'
    )
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_geofences'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Geofence'
        verbose_name_plural = 'Geofences'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    def get_polygon_coordinates(self):
        """Extract coordinates from GeoJSON polygon"""
        try:
            if isinstance(self.polygon_json, dict):
                if self.polygon_json.get('type') == 'Polygon':
                    return self.polygon_json.get('coordinates', [])
                elif self.polygon_json.get('type') == 'Feature':
                    geometry = self.polygon_json.get('geometry', {})
                    if geometry.get('type') == 'Polygon':
                        return geometry.get('coordinates', [])
            return []
        except (json.JSONDecodeError, AttributeError):
            return []
    
    def get_center_point(self):
        """Calculate center point of the polygon"""
        coordinates = self.get_polygon_coordinates()
        if not coordinates or not coordinates[0]:
            return None
        
        # Get the first ring of the polygon
        ring = coordinates[0]
        if not ring:
            return None
        
        # Calculate center
        lats = [coord[1] for coord in ring]
        lons = [coord[0] for coord in ring]
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        return [center_lon, center_lat]


class Alert(models.Model):
    ALERT_TYPES = [
        ('GEOFENCE_ENTER', 'Geofence Enter'),
        ('GEOFENCE_EXIT', 'Geofence Exit'),
        ('GEOFENCE_VIOLATION', 'Geofence Violation'),
        ('SYSTEM_ERROR', 'System Error'),
        ('SECURITY_BREACH', 'Security Breach'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        default='GEOFENCE_ENTER'
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
    
    def resolve(self, resolved_by_user):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by_user
        self.save()


class SecurityOfficer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20, help_text="Phone number or contact info")
    email = models.EmailField(blank=True, null=True)
    assigned_geofence = models.ForeignKey(
        Geofence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_officers'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='security_officers'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_officers',
        limit_choices_to={'role': 'SUB_ADMIN'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Security Officer'
        verbose_name_plural = 'Security Officers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Incident(models.Model):
    INCIDENT_TYPES = [
        ('SECURITY_BREACH', 'Security Breach'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('EMERGENCY', 'Emergency'),
        ('MAINTENANCE', 'Maintenance'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.CASCADE,
        related_name='incidents'
    )
    officer = models.ForeignKey(
        SecurityOfficer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_incidents'
    )
    incident_type = models.CharField(
        max_length=20,
        choices=INCIDENT_TYPES,
        default='SUSPICIOUS_ACTIVITY'
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    title = models.CharField(max_length=200)
    details = models.TextField()
    location = models.JSONField(
        default=dict,
        help_text="GPS coordinates and location details"
    )
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_incidents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
    
    def resolve(self, resolved_by_user):
        """Mark incident as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by_user
        self.save()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('NORMAL', 'Normal'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    TARGET_TYPES = [
        ('ALL_OFFICERS', 'All Officers'),
        ('GEOFENCE_OFFICERS', 'Geofence Officers'),
        ('SPECIFIC_OFFICERS', 'Specific Officers'),
        ('SUB_ADMIN', 'Sub Admin Only'),
    ]
    
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='NORMAL'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPES,
        default='ALL_OFFICERS'
    )
    target_geofence = models.ForeignKey(
        Geofence,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    target_officers = models.ManyToManyField(
        SecurityOfficer,
        blank=True,
        related_name='received_notifications'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_notifications',
        limit_choices_to={'role': 'SUB_ADMIN'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.notification_type})"
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()


class GlobalReport(models.Model):
    REPORT_TYPES = [
        ('GEOFENCE_ANALYTICS', 'Geofence Analytics'),
        ('USER_ACTIVITY', 'User Activity'),
        ('ALERT_SUMMARY', 'Alert Summary'),
        ('SYSTEM_HEALTH', 'System Health'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        default='GEOFENCE_ANALYTICS'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    metrics = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Global Report'
        verbose_name_plural = 'Global Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"
    
    def mark_as_generated(self, file_path=None):
        """Mark report as generated"""
        self.is_generated = True
        self.generated_at = timezone.now()
        if file_path:
            self.file_path = file_path
        self.save()
