# SafeTNet Admin Panel API - cURL Examples
# Base URL: http://localhost:8000/api

# =============================================================================
# AUTHENTICATION
# =============================================================================

# 1. Register a new user
curl -X POST "http://localhost:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "StrongPass123!",
    "first_name": "New",
    "last_name": "User",
    "role": "USER",
    "organization": 1
  }'

# 2. Login and get tokens
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "superadmin",
    "password": "testpass123!"
  }'

# Response will contain access and refresh tokens
# Save the access token for subsequent requests

# 3. Refresh access token
curl -X POST "http://localhost:8000/api/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'

# 4. Get user profile
curl -X GET "http://localhost:8000/api/auth/profile/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5. Logout
curl -X POST "http://localhost:8000/api/auth/logout/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# ORGANIZATIONS (Super Admin only)
# =============================================================================

# 1. List all organizations
curl -X GET "http://localhost:8000/api/auth/admin/organizations/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Create new organization
curl -X POST "http://localhost:8000/api/auth/admin/organizations/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Organization",
    "description": "A new organization for testing"
  }'

# 3. Get specific organization
curl -X GET "http://localhost:8000/api/auth/admin/organizations/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Update organization
curl -X PUT "http://localhost:8000/api/auth/admin/organizations/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Organization",
    "description": "Updated description"
  }'

# 5. Delete organization
curl -X DELETE "http://localhost:8000/api/auth/admin/organizations/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# SUB-ADMINS (Super Admin only)
# =============================================================================

# 1. List all sub-admins
curl -X GET "http://localhost:8000/api/auth/admin/subadmins/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Create new sub-admin
curl -X POST "http://localhost:8000/api/auth/admin/subadmins/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newsubadmin",
    "email": "subadmin@example.com",
    "password": "StrongPass123!",
    "first_name": "Sub",
    "last_name": "Admin",
    "organization": 1
  }'

# 3. Get specific sub-admin
curl -X GET "http://localhost:8000/api/auth/admin/subadmins/2/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Update sub-admin
curl -X PUT "http://localhost:8000/api/auth/admin/subadmins/2/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updatedsubadmin",
    "email": "updated@example.com",
    "first_name": "Updated",
    "last_name": "Admin",
    "organization": 1
  }'

# 5. Delete sub-admin
curl -X DELETE "http://localhost:8000/api/auth/admin/subadmins/2/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# GEOFENCES
# =============================================================================

# 1. List all geofences (organization-filtered for Sub-Admins)
curl -X GET "http://localhost:8000/api/auth/admin/geofences/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Create new geofence
curl -X POST "http://localhost:8000/api/auth/admin/geofences/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Geofence",
    "description": "A new geofence for testing",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 100,
    "active": true,
    "organization": 1
  }'

# 3. Get specific geofence
curl -X GET "http://localhost:8000/api/auth/admin/geofences/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Update geofence
curl -X PUT "http://localhost:8000/api/auth/admin/geofences/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Geofence",
    "description": "Updated description",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 150,
    "active": true,
    "organization": 1
  }'

# 5. Delete geofence
curl -X DELETE "http://localhost:8000/api/auth/admin/geofences/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# USERS
# =============================================================================

# 1. List all users (organization-filtered for Sub-Admins)
curl -X GET "http://localhost:8000/api/auth/admin/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Get specific user
curl -X GET "http://localhost:8000/api/auth/admin/users/4/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# ALERTS
# =============================================================================

# 1. List all alerts (organization-filtered for Sub-Admins)
curl -X GET "http://localhost:8000/api/auth/admin/alerts/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. List alerts with filters
curl -X GET "http://localhost:8000/api/auth/admin/alerts/?severity=HIGH&is_resolved=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Create new alert
curl -X POST "http://localhost:8000/api/auth/admin/alerts/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Alert",
    "description": "This is a test alert",
    "alert_type": "GEOFENCE_ENTER",
    "severity": "MEDIUM",
    "geofence": 1,
    "user": 4,
    "metadata": {
      "test": true,
      "source": "api"
    }
  }'

# 4. Get specific alert
curl -X GET "http://localhost:8000/api/auth/admin/alerts/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5. Update alert
curl -X PUT "http://localhost:8000/api/auth/admin/alerts/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Alert",
    "description": "Updated description",
    "alert_type": "GEOFENCE_ENTER",
    "severity": "HIGH",
    "geofence": 1,
    "user": 4,
    "metadata": {
      "updated": true
    }
  }'

# 6. Resolve alert (partial update)
curl -X PATCH "http://localhost:8000/api/auth/admin/alerts/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_resolved": true
  }'

# 7. Delete alert
curl -X DELETE "http://localhost:8000/api/auth/admin/alerts/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# REPORTS (Super Admin only)
# =============================================================================

# 1. List all reports
curl -X GET "http://localhost:8000/api/auth/admin/reports/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Create new report
curl -X POST "http://localhost:8000/api/auth/admin/reports/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "description": "This is a test report",
    "report_type": "GEOFENCE_ANALYTICS",
    "date_range_start": "2024-01-01T00:00:00Z",
    "date_range_end": "2024-01-31T23:59:59Z"
  }'

# 3. Generate report with metrics
curl -X POST "http://localhost:8000/api/auth/reports/generate/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "GEOFENCE_ANALYTICS",
    "date_range_start": "2024-01-01T00:00:00Z",
    "date_range_end": "2024-01-31T23:59:59Z",
    "title": "Generated Report"
  }'

# 4. Get specific report
curl -X GET "http://localhost:8000/api/auth/admin/reports/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5. Download report as CSV
curl -X GET "http://localhost:8000/api/auth/reports/1/download/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -o "report.csv"

# 6. Delete report
curl -X DELETE "http://localhost:8000/api/auth/admin/reports/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# DASHBOARD
# =============================================================================

# 1. Get dashboard KPIs
curl -X GET "http://localhost:8000/api/auth/dashboard-kpis/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# =============================================================================
# API DOCUMENTATION
# =============================================================================

# 1. Get OpenAPI schema
curl -X GET "http://localhost:8000/api/schema/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. Access Swagger UI (in browser)
# http://localhost:8000/api/docs/

# 3. Access ReDoc (in browser)
# http://localhost:8000/api/redoc/

# =============================================================================
# ERROR HANDLING EXAMPLES
# =============================================================================

# 1. Unauthorized access (no token)
curl -X GET "http://localhost:8000/api/auth/admin/alerts/"

# 2. Invalid token
curl -X GET "http://localhost:8000/api/auth/admin/alerts/" \
  -H "Authorization: Bearer invalid_token"

# 3. Insufficient permissions (Sub-Admin trying to create report)
curl -X POST "http://localhost:8000/api/auth/admin/reports/" \
  -H "Authorization: Bearer SUB_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "report_type": "GEOFENCE_ANALYTICS",
    "date_range_start": "2024-01-01T00:00:00Z",
    "date_range_end": "2024-01-31T23:59:59Z"
  }'

# 4. Validation error (invalid email)
curl -X POST "http://localhost:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "invalid-email",
    "password": "StrongPass123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "USER",
    "organization": 1
  }'

# =============================================================================
# BATCH OPERATIONS
# =============================================================================

# 1. Create multiple alerts
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/auth/admin/alerts/" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Batch Alert $i\",
      \"description\": \"Batch alert number $i\",
      \"alert_type\": \"GEOFENCE_ENTER\",
      \"severity\": \"MEDIUM\",
      \"geofence\": 1,
      \"user\": 4
    }"
done

# 2. Resolve multiple alerts
for i in {1..5}; do
  curl -X PATCH "http://localhost:8000/api/auth/admin/alerts/$i/" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"is_resolved": true}'
done

# =============================================================================
# PERFORMANCE TESTING
# =============================================================================

# 1. Load test alerts endpoint
for i in {1..100}; do
  curl -X GET "http://localhost:8000/api/auth/admin/alerts/" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" &
done
wait

# 2. Concurrent alert creation
for i in {1..20}; do
  curl -X POST "http://localhost:8000/api/auth/admin/alerts/" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"Concurrent Alert $i\",
      \"description\": \"Concurrent alert number $i\",
      \"alert_type\": \"GEOFENCE_ENTER\",
      \"severity\": \"LOW\",
      \"geofence\": 1
    }" &
done
wait
