from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, SubAdminProfile, Organization, Geofence, Alert, GlobalReport, SecurityOfficer, Incident, Notification


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role')
        extra_kwargs = {
            'role': {'required': False}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class SubAdminProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SubAdminProfile
        fields = (
            'id', 'user', 'user_username', 'user_email', 'user_full_name',
            'permissions', 'assigned_scope', 'is_active', 
            'created_by_username', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by_username', 'created_at', 'updated_at')
    
    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class SubAdminProfileCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = SubAdminProfile
        fields = (
            'username', 'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'permissions', 'assigned_scope', 'is_active'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        # Create user first
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'role': 'SUB_ADMIN'
        }
        
        user = User.objects.create_user(**user_data)
        
        # Create SubAdminProfile
        profile_data = {
            'user': user,
            'permissions': validated_data['permissions'],
            'assigned_scope': validated_data['assigned_scope'],
            'is_active': validated_data['is_active'],
            'created_by': self.context['request'].user
        }
        
        return SubAdminProfile.objects.create(**profile_data)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class GeofenceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    center_point = serializers.SerializerMethodField()
    
    class Meta:
        model = Geofence
        fields = (
            'id', 'name', 'description', 'polygon_json', 'organization', 
            'organization_name', 'active', 'created_by_username', 
            'created_at', 'updated_at', 'center_point'
        )
        read_only_fields = ('id', 'created_by_username', 'created_at', 'updated_at', 'center_point')
    
    def get_center_point(self, obj):
        return obj.get_center_point()


class GeofenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = ('name', 'description', 'polygon_json', 'organization', 'active')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class UserListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'organization', 'organization_name', 'is_active', 
        'date_joined', 'last_login'
    )
    read_only_fields = ('id', 'date_joined', 'last_login')


class AlertSerializer(serializers.ModelSerializer):
    geofence_name = serializers.CharField(source='geofence.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = (
            'id', 'geofence', 'geofence_name', 'user', 'user_username',
            'alert_type', 'severity', 'title', 'description', 'metadata',
            'is_resolved', 'resolved_at', 'resolved_by_username',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'resolved_at')


class AlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            'geofence', 'user', 'alert_type', 'severity', 'title', 
            'description', 'metadata'
        )


class GlobalReportSerializer(serializers.ModelSerializer):
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = GlobalReport
        fields = (
            'id', 'report_type', 'title', 'description', 'date_range_start',
            'date_range_end', 'metrics', 'file_path', 'generated_by_username',
            'is_generated', 'generated_at', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'generated_by_username', 'generated_at', 'created_at', 'updated_at')


class GlobalReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalReport
        fields = (
            'report_type', 'title', 'description', 'date_range_start', 'date_range_end'
        )
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)


# Sub-Admin Panel Serializers
class SecurityOfficerSerializer(serializers.ModelSerializer):
    assigned_geofence_name = serializers.CharField(source='assigned_geofence.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SecurityOfficer
        fields = (
            'id', 'name', 'contact', 'email', 'assigned_geofence', 
            'assigned_geofence_name', 'organization', 'organization_name',
            'is_active', 'created_by_username', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by_username', 'created_at', 'updated_at')


class SecurityOfficerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityOfficer
        fields = ('name', 'contact', 'email', 'assigned_geofence', 'is_active')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['organization'] = self.context['request'].user.organization
        return super().create(validated_data)


class IncidentSerializer(serializers.ModelSerializer):
    geofence_name = serializers.CharField(source='geofence.name', read_only=True)
    officer_name = serializers.CharField(source='officer.name', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = Incident
        fields = (
            'id', 'geofence', 'geofence_name', 'officer', 'officer_name',
            'incident_type', 'severity', 'title', 'details', 'location',
            'is_resolved', 'resolved_at', 'resolved_by_username',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'resolved_at', 'created_at', 'updated_at')


class IncidentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = (
            'geofence', 'officer', 'incident_type', 'severity', 
            'title', 'details', 'location'
        )


class NotificationSerializer(serializers.ModelSerializer):
    target_geofence_name = serializers.CharField(source='target_geofence.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    target_officers_names = serializers.StringRelatedField(source='target_officers', many=True, read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'notification_type', 'title', 'message', 'target_type',
            'target_geofence', 'target_geofence_name', 'target_officers',
            'target_officers_names', 'organization', 'organization_name',
            'is_sent', 'sent_at', 'created_by_username', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'sent_at', 'created_by_username', 'created_at', 'updated_at')


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'notification_type', 'title', 'message', 'target_type',
            'target_geofence', 'target_officers'
        )
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['organization'] = self.context['request'].user.organization
        return super().create(validated_data)


class NotificationSendSerializer(serializers.Serializer):
    """Serializer for sending notifications"""
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    target_type = serializers.ChoiceField(choices=Notification.TARGET_TYPES)
    target_geofence_id = serializers.IntegerField(required=False, allow_null=True)
    target_officer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_target_geofence_id(self, value):
        if value:
            try:
                geofence = Geofence.objects.get(id=value)
                # Ensure the geofence belongs to the user's organization
                if geofence.organization != self.context['request'].user.organization:
                    raise serializers.ValidationError("Geofence does not belong to your organization.")
            except Geofence.DoesNotExist:
                raise serializers.ValidationError("Geofence not found.")
        return value
    
    def validate_target_officer_ids(self, value):
        if value:
            officers = SecurityOfficer.objects.filter(
                id__in=value,
                organization=self.context['request'].user.organization
            )
            if len(officers) != len(value):
                raise serializers.ValidationError("Some officers do not belong to your organization.")
        return value
