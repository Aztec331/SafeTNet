# Navigation API Documentation

## Overview
The Navigation API provides route calculation between two coordinates using Google Maps Directions API with fallback to haversine distance calculation.

## Endpoint
**POST** `/api/security/navigation/`

## Authentication
Requires JWT authentication and security officer role.

## Request Format

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
    "from_lat": 18.5204,
    "from_lng": 73.8567,
    "to_lat": 18.5310,
    "to_lng": 73.8440
}
```

### Parameters
- `from_lat` (float, required): Officer's current latitude
- `from_lng` (float, required): Officer's current longitude  
- `to_lat` (float, required): Target location latitude
- `to_lng` (float, required): Target location longitude

## Response Format

### Success Response (200 OK)
```json
{
    "from_location": {
        "lat": 18.5204,
        "lng": 73.8567
    },
    "to_location": {
        "lat": 18.5310,
        "lng": 73.8440
    },
    "route": {
        "distance_km": 2.5,
        "duration_minutes": 8.5,
        "polyline": "encoded_polyline_string_here",
        "steps": [
            {
                "instruction": "Head north on Main Street",
                "distance": "500 m",
                "duration": "2 mins"
            },
            {
                "instruction": "Turn right onto Oak Avenue",
                "distance": "1.2 km", 
                "duration": "4 mins"
            }
        ],
        "summary": "2.5 km - 8 mins"
    }
}
```

### Fallback Response (when Google Maps API is not configured)
```json
{
    "from_location": {
        "lat": 18.5204,
        "lng": 73.8567
    },
    "to_location": {
        "lat": 18.5310,
        "lng": 73.8440
    },
    "route": {
        "distance_km": 1.8,
        "duration_minutes": 3,
        "polyline": null,
        "steps": [
            "Head towards target using best available route",
            "Follow primary roads",
            "Adjust path as needed"
        ],
        "summary": "1.8 km - Estimated 3 minutes",
        "note": "Route calculated using straight-line distance. For detailed directions, configure Google Maps API key."
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid or missing coordinates. Expected: from_lat, from_lng, to_lat, to_lng"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "Only security officers can access this resource."
}
```

### 500 Internal Server Error
```json
{
    "error": "Google Maps API error: REQUEST_DENIED"
}
```

## Configuration

### Google Maps API Setup
1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Directions API
3. Set the API key in your environment variables:
   ```bash
   export GOOGLE_MAPS_API_KEY="your_api_key_here"
   ```
4. Or add it to your `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

### API Key Permissions
The API key needs the following APIs enabled:
- Directions API
- Maps JavaScript API (if using frontend maps)

## Example Usage

### cURL Example
```bash
curl -X POST http://localhost:8000/api/security/navigation/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "from_lat": 18.5204,
    "from_lng": 73.8567,
    "to_lat": 18.5310,
    "to_lng": 73.8440
  }'
```

### JavaScript Example
```javascript
const getRoute = async (fromLat, fromLng, toLat, toLng) => {
    const response = await fetch('/api/security/navigation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            from_lat: fromLat,
            from_lng: fromLng,
            to_lat: toLat,
            to_lng: toLng
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log('Route:', data.route);
        return data;
    } else {
        const error = await response.json();
        console.error('Navigation error:', error);
    }
};
```

## Features

### With Google Maps API
- Real-time route calculation
- Traffic-aware ETA
- Detailed turn-by-turn directions
- Encoded polyline for map rendering
- Multiple transportation modes (driving, walking, cycling, transit)

### Fallback Mode (without API key)
- Straight-line distance calculation
- Estimated ETA based on average speed
- Basic route guidance
- No polyline data

## Rate Limits
- Google Maps API has usage limits based on your billing plan
- Free tier: 2,500 requests per day
- Consider implementing caching for frequently requested routes

## Security Notes
- API key should be kept secure and not exposed in frontend code
- Consider implementing request rate limiting
- Validate coordinate ranges to prevent abuse
