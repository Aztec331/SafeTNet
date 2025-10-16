# Security App - SOS Alert API Documentation

## Overview
The Security app provides APIs for managing SOS (Save Our Souls) alerts. Users can trigger emergency alerts with their location, and administrators can view and manage these alerts.

## Endpoints

### Base URL
```
/api/security/
```

## SOS Alert Endpoints

### 1. Create SOS Alert
**POST** `/api/security/sos/`

Creates a new SOS alert. Any authenticated user can create an SOS alert.

**Request Body:**
```json
{
    "location_lat": 40.7128,
    "location_long": -74.0060,
    "message": "Emergency! I need help immediately!"
}
```

**Response (201 Created):**
```json
{
    "location_lat": 40.7128,
    "location_long": -74.0060,
    "message": "Emergency! I need help immediately!"
}
```

**Authentication:** Required (JWT Token)

### 2. List All SOS Alerts
**GET** `/api/security/sos/`

Lists all SOS alerts. Only admin and sub-admin users can access this endpoint.

**Query Parameters:**
- `status`: Filter by status (`active` or `resolved`)
- `user`: Filter by user ID
- `search`: Search in username, email, or message
- `ordering`: Order by field (e.g., `-created_at` for newest first)

**Response (200 OK):**
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
        }
    ]
}
```

**Authentication:** Required (Admin/Sub-Admin only)

### 3. Get Active SOS Alerts
**GET** `/api/security/sos/active/`

Gets all active (unresolved) SOS alerts.

**Response (200 OK):**
```json
[
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
    }
]
```

**Authentication:** Required (Admin/Sub-Admin only)

### 4. Get Resolved SOS Alerts
**GET** `/api/security/sos/resolved/`

Gets all resolved SOS alerts.

**Response (200 OK):**
```json
[
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
```

**Authentication:** Required (Admin/Sub-Admin only)

### 5. Resolve SOS Alert
**PATCH** `/api/security/sos/{id}/resolve/`

Marks an SOS alert as resolved.

**Response (200 OK):**
```json
{
    "id": 1,
    "user": 1,
    "user_username": "john_doe",
    "user_email": "john@example.com",
    "location_lat": 40.7128,
    "location_long": -74.0060,
    "message": "Emergency! I need help immediately!",
    "status": "resolved",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
}
```

**Authentication:** Required (Admin/Sub-Admin only)

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Permissions

- **Users**: Can create SOS alerts
- **Sub-Admins**: Can view and manage SOS alerts from their organization
- **Super-Admins**: Can view and manage all SOS alerts

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 400 Bad Request
```json
{
    "location_lat": ["This field is required."],
    "location_long": ["This field is required."]
}
```

## Example Usage

### Creating an SOS Alert (JavaScript)
```javascript
const createSOSAlert = async (lat, lng, message) => {
    const response = await fetch('/api/security/sos/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            location_lat: lat,
            location_long: lng,
            message: message
        })
    });
    
    if (response.ok) {
        const alert = await response.json();
        console.log('SOS Alert created:', alert);
    }
};
```

### Listing Active Alerts (Admin)
```javascript
const getActiveAlerts = async () => {
    const response = await fetch('/api/security/sos/active/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    
    if (response.ok) {
        const alerts = await response.json();
        console.log('Active alerts:', alerts);
    }
};
```

### Resolving an Alert
```javascript
const resolveAlert = async (alertId) => {
    const response = await fetch(`/api/security/sos/${alertId}/resolve/`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    
    if (response.ok) {
        const alert = await response.json();
        console.log('Alert resolved:', alert);
    }
};
```

## Model Fields

### SOSAlert Model
- `id`: Primary key (auto-generated)
- `user`: Foreign key to User model
- `location_lat`: Latitude coordinate (FloatField)
- `location_long`: Longitude coordinate (FloatField)
- `message`: Optional message from user (TextField)
- `status`: Alert status - 'active' or 'resolved' (CharField)
- `created_at`: Timestamp when alert was created (DateTimeField)
- `updated_at`: Timestamp when alert was last updated (DateTimeField)

## Database Migration

The SOSAlert model has been created and migrated. The migration file is located at:
```
security/migrations/0001_initial.py
```

## Testing

Run the security app tests with:
```bash
python manage.py test security
```

The test suite includes:
- Model creation tests
- API endpoint tests
- Permission tests
- Authentication tests
