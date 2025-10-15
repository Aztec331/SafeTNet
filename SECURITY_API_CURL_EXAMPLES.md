# Security App - SOS Alert API cURL Examples

## Prerequisites
1. Get a JWT token by logging in first:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

2. Use the `access` token from the response in subsequent requests.

## SOS Alert API Examples

### 1. Create SOS Alert
```bash
curl -X POST http://localhost:8000/api/security/sos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "location_lat": 40.7128,
    "location_long": -74.0060,
    "message": "Emergency! I need help immediately!"
  }'
```

### 2. List All SOS Alerts (Admin/Sub-Admin only)
```bash
curl -X GET http://localhost:8000/api/security/sos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. List Active SOS Alerts
```bash
curl -X GET http://localhost:8000/api/security/sos/active/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. List Resolved SOS Alerts
```bash
curl -X GET http://localhost:8000/api/security/sos/resolved/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Resolve SOS Alert
```bash
curl -X PATCH http://localhost:8000/api/security/sos/1/resolve/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Filter Alerts by Status
```bash
curl -X GET "http://localhost:8000/api/security/sos/?status=active" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Search Alerts
```bash
curl -X GET "http://localhost:8000/api/security/sos/?search=emergency" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. Order Alerts by Creation Date (newest first)
```bash
curl -X GET "http://localhost:8000/api/security/sos/?ordering=-created_at" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Complete Workflow Example

### Step 1: Login and get token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }' | jq -r '.access')
```

### Step 2: Create SOS Alert
```bash
curl -X POST http://localhost:8000/api/security/sos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "location_lat": 40.7128,
    "location_long": -74.0060,
    "message": "Help! I am in danger!"
  }'
```

### Step 3: List all alerts (as admin)
```bash
curl -X GET http://localhost:8000/api/security/sos/ \
  -H "Authorization: Bearer $TOKEN"
```

### Step 4: Resolve the alert (as admin)
```bash
curl -X PATCH http://localhost:8000/api/security/sos/1/resolve/ \
  -H "Authorization: Bearer $TOKEN"
```

## Error Examples

### Unauthorized Access (no token)
```bash
curl -X GET http://localhost:8000/api/security/sos/
# Returns: 401 Unauthorized
```

### Forbidden Access (regular user trying to list alerts)
```bash
curl -X GET http://localhost:8000/api/security/sos/ \
  -H "Authorization: Bearer USER_TOKEN"
# Returns: 403 Forbidden
```

### Invalid Data
```bash
curl -X POST http://localhost:8000/api/security/sos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "location_lat": "invalid",
    "location_long": -74.0060
  }'
# Returns: 400 Bad Request with validation errors
```

## Response Examples

### Successful SOS Alert Creation
```json
{
  "location_lat": 40.7128,
  "location_long": -74.0060,
  "message": "Emergency! I need help immediately!"
}
```

### SOS Alert List Response
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_username": "john_doe",
      "user_email": "john@example.com",
      "location_lat": 40.7128,
      "location_long": -74.0060,
      "message": "Emergency! I need help immediately!",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "user": 2,
      "user_username": "jane_doe",
      "user_email": "jane@example.com",
      "location_lat": 40.7589,
      "location_long": -73.9851,
      "message": "Help needed at Central Park",
      "status": "resolved",
      "created_at": "2024-01-15T09:15:00Z",
      "updated_at": "2024-01-15T11:45:00Z"
    }
  ]
}
```

### Error Response
```json
{
  "location_lat": ["This field is required."],
  "location_long": ["This field is required."]
}
```
