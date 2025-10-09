# SafeTNet Sub-Admin Panel - Complete Implementation Guide

## Overview

The Sub-Admin Panel is a companion application to the Main-Admin-Panel that allows Sub-Administrators to manage their assigned geofences, security officers, and incidents while maintaining strict data isolation from other organizations.

## 🚀 Features Implemented

### 1. **Authentication & Authorization**
- JWT-based authentication using the same auth server as Main-Admin
- Role-based access control (only SUB_ADMIN role can access)
- Automatic token refresh
- Secure logout functionality

### 2. **Dashboard**
- Real-time KPIs for the Sub-Admin's organization
- Active geofences count
- Total and active officers count
- Incidents today, unresolved, and critical incidents
- Notifications sent today
- Quick action buttons for common tasks

### 3. **Geofence Management**
- Interactive map with Leaflet integration
- Draw polygons by clicking on the map
- Create, edit, and delete geofences
- View existing geofences with different colors for active/inactive
- Organization-specific geofence isolation

### 4. **Security Officer Management**
- Create, edit, and delete security officers
- Assign officers to specific geofences
- Activate/deactivate officer accounts
- Contact information management
- Organization-specific officer isolation

### 5. **Incident Management**
- Report and track security incidents
- Multiple incident types (Security Breach, Unauthorized Access, etc.)
- Severity levels (Low, Medium, High, Critical)
- Assign incidents to specific officers
- Mark incidents as resolved
- Organization-specific incident isolation

### 6. **Notification System**
- Send notifications to officers
- Two notification types:
  - **Normal**: Regular push notification
  - **Emergency**: Siren-tone alert that overrides silent mode
- Multiple target types:
  - All Officers
  - Geofence-specific Officers
  - Specific Officers
  - Sub-Admin Only
- Track notification history

## 🏗️ Technical Architecture

### Backend (Django + DRF)

#### New Models Added:
```python
class SecurityOfficer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    assigned_geofence = models.ForeignKey(Geofence, ...)
    organization = models.ForeignKey(Organization, ...)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, ...)

class Incident(models.Model):
    geofence = models.ForeignKey(Geofence, ...)
    officer = models.ForeignKey(SecurityOfficer, ...)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    details = models.TextField()
    location = models.JSONField(default=dict)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, ...)

class Notification(models.Model):
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    target_geofence = models.ForeignKey(Geofence, ...)
    target_officers = models.ManyToManyField(SecurityOfficer, ...)
    organization = models.ForeignKey(Organization, ...)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, ...)
```

#### API Endpoints:
```
GET    /api/admin/geofences/              # List geofences
POST   /api/admin/geofences/              # Create geofence
PUT    /api/admin/geofences/{id}/         # Update geofence
DELETE /api/admin/geofences/{id}/         # Delete geofence

GET    /api/admin/officers/               # List officers
POST   /api/admin/officers/               # Create officer
PUT    /api/admin/officers/{id}/          # Update officer
DELETE /api/admin/officers/{id}/          # Delete officer

GET    /api/admin/incidents/              # List incidents
POST   /api/admin/incidents/              # Create incident
PUT    /api/admin/incidents/{id}/         # Update incident
POST   /api/admin/incidents/{id}/resolve/ # Resolve incident

GET    /api/admin/notifications/          # List notifications
POST   /api/subadmin/notifications/send/  # Send notification

GET    /api/subadmin/dashboard-kpis/      # Get dashboard KPIs
```

### Frontend (React + TypeScript)

#### Key Components:
- **AuthContext**: JWT authentication management
- **ProtectedRoute**: Route protection for Sub-Admins only
- **Layout**: Main layout with sidebar navigation
- **Dashboard**: KPI overview and quick actions
- **Geofences**: Interactive map with polygon drawing
- **Officers**: Officer management with assignments
- **Incidents**: Incident tracking and resolution
- **Notifications**: Notification sending and history

#### Technology Stack:
- React 18 with TypeScript
- React Router for navigation
- Tailwind CSS for styling
- Leaflet for map integration
- Axios for API communication
- React Hook Form for form handling
- Lucide React for icons

## 🔒 Data Isolation

All queries are filtered by the Sub-Admin's organization to ensure strict data isolation:

```python
# Example from SecurityOfficerViewSet
def get_queryset(self):
    queryset = super().get_queryset()
    user = self.request.user
    
    # SUPER_ADMIN can see all officers
    if user.role == 'SUPER_ADMIN':
        return queryset
    
    # SUB_ADMIN can only see officers from their organization
    if user.role == 'SUB_ADMIN' and user.organization:
        return queryset.filter(organization=user.organization)
    
    return queryset.none()
```

## 🗺️ Map Integration

The geofence management includes interactive map functionality:

1. **Leaflet Integration**: Uses OpenStreetMap tiles
2. **Polygon Drawing**: Click-to-draw polygon creation
3. **Visual Feedback**: Different colors for active/inactive geofences
4. **Popup Information**: Click on geofences to see details
5. **Center Point Calculation**: Automatic center point calculation for geofences

## 📱 Notification System

### Notification Types:
- **Normal**: Regular push notification
- **Emergency**: Urgent alert with siren tone

### Target Types:
- **All Officers**: Send to all active officers in organization
- **Geofence Officers**: Send to officers assigned to specific geofence
- **Specific Officers**: Send to selected officers
- **Sub Admin Only**: Send to sub-admin only

### Implementation:
```typescript
const sendNotification = async (data: NotificationSendData) => {
  const response = await api.post('/subadmin/notifications/send/', data);
  return response.data;
};
```

## 🚀 Getting Started

### Prerequisites:
- Python 3.8+
- Node.js 16+
- Django backend running on http://localhost:8000

### Backend Setup:
```bash
cd SafeTNet
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Frontend Setup:
```bash
cd subadmin-ui
npm install
npm start
```

### Environment Variables:
Create `.env.local` in subadmin-ui directory:
```
REACT_APP_API_URL=http://localhost:8000/api
```

## 🔐 Authentication Flow

1. User logs in with username/password
2. Backend validates credentials and returns JWT tokens
3. Frontend stores access and refresh tokens
4. All API requests include Bearer token in Authorization header
5. Token automatically refreshed when expired
6. Logout clears tokens and redirects to login

## 📊 Dashboard KPIs

The dashboard provides real-time metrics:
- Active geofences count
- Total and active officers
- Incidents today, unresolved, and critical
- Notifications sent today
- Organization name display

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile
- **Loading States**: Proper loading indicators
- **Error Handling**: User-friendly error messages
- **Form Validation**: Client-side validation
- **Modal Forms**: Clean modal-based forms
- **Status Indicators**: Visual status indicators
- **Quick Actions**: Dashboard quick action buttons

## 🔧 Development Notes

### Key Files:
- `users/models.py`: New models for Sub-Admin functionality
- `users/views.py`: API views with organization isolation
- `users/serializers.py`: DRF serializers for new models
- `users/urls.py`: URL routing for Sub-Admin endpoints
- `subadmin-ui/src/`: Complete React frontend

### Database Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing:
- Backend: Django test framework
- Frontend: React Testing Library (can be added)

## 🚀 Deployment

### Backend:
- Deploy Django app to your preferred hosting service
- Set up PostgreSQL database
- Configure environment variables
- Run migrations

### Frontend:
- Build React app: `npm run build`
- Deploy to static hosting (Vercel, Netlify, etc.)
- Update API URL for production

## 📝 API Documentation

The API follows RESTful conventions and includes:
- Proper HTTP status codes
- Pagination for list endpoints
- Filtering and searching capabilities
- Comprehensive error responses
- JWT authentication

## 🔮 Future Enhancements

1. **Real-time Updates**: WebSocket integration for live updates
2. **Push Notifications**: FCM integration for mobile notifications
3. **Advanced Analytics**: More detailed reporting and analytics
4. **Mobile App**: React Native mobile application
5. **Offline Support**: PWA capabilities
6. **Advanced Map Features**: More map tools and overlays

## 🐛 Troubleshooting

### Common Issues:
1. **CORS Errors**: Ensure CORS is configured in Django settings
2. **Token Expiry**: Check JWT token lifetime settings
3. **Map Not Loading**: Verify Leaflet CSS and JS are loaded
4. **API Connection**: Check API URL and network connectivity

### Debug Mode:
- Backend: Set `DEBUG=True` in Django settings
- Frontend: Use React Developer Tools

## 📞 Support

For issues or questions:
1. Check the logs in Django console
2. Use browser developer tools for frontend debugging
3. Verify API endpoints with Postman or similar tools
4. Check database migrations are applied correctly

---

The Sub-Admin Panel is now fully functional and ready for use! 🎉
