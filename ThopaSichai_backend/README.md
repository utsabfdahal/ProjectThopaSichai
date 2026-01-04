# ThopaSichai Backend - Authentication API

Django REST Framework backend with token-based authentication for Thopa Sichai Irrigation System.

## 🚀 Quick Start

### Server is Running
- **URL**: `http://10.164.63.195:8000/` or `http://localhost:8000/`
- **Status**: ✅ Running in background (PID: 39922)

### Stop Server
```bash
pkill -f "manage.py runserver"
```

### Start Server
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python manage.py runserver 0.0.0.0:8000
```

## 📡 API Endpoints

### 1. Register New User
**Endpoint**: `POST /api/auth/register/`

**Request Body**:
```json
{
    "username": "farmer1",
    "email": "farmer1@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response** (201 Created):
```json
{
    "token": "ce0a0d6d69025b72cc5025113cab649149de967b",
    "user": {
        "id": 1,
        "username": "farmer1",
        "email": "farmer1@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "message": "Registration successful!"
}
```

**Test with curl**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","email":"farmer1@example.com","password":"testpass123","password2":"testpass123","first_name":"John","last_name":"Doe"}'
```

### 2. Login
**Endpoint**: `POST /api/auth/login/`

**Request Body**:
```json
{
    "username": "farmer1",
    "password": "testpass123"
}
```

**Response** (200 OK):
```json
{
    "token": "ce0a0d6d69025b72cc5025113cab649149de967b",
    "user": {
        "id": 1,
        "username": "farmer1",
        "email": "farmer1@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "message": "Login successful!"
}
```

**Response** (401 Unauthorized - wrong password):
```json
{
    "error": "Invalid username or password"
}
```

**Test with curl**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"testpass123"}'
```

### 3. Get User Profile
**Endpoint**: `GET /api/auth/profile/`

**Headers**:
```
Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b
```

**Response** (200 OK):
```json
{
    "id": 1,
    "username": "farmer1",
    "email": "farmer1@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Test with curl**:
```bash
curl -X GET http://10.164.63.195:8000/api/auth/profile/ \
  -H "Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b"
```

### 4. Logout
**Endpoint**: `POST /api/auth/logout/`

**Headers**:
```
Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b
```

**Response** (200 OK):
```json
{
    "message": "Logout successful!"
}
```

## 🔐 Authentication Flow

1. **Register**: User creates account → Receives token
2. **Login**: User logs in → Receives same/new token
3. **Authenticated Requests**: Include token in header
   ```
   Authorization: Token <your-token-here>
   ```
4. **Logout**: Deletes token from server

## 📱 Flutter Integration

### Update Flutter App Base URL

In your Flutter app, use this base URL:
```dart
const String baseUrl = 'http://10.164.63.195:8000';
```

### Add HTTP Package
```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
```

### Example Login Code
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('http://10.164.63.195:8000/api/auth/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'password': password,
    }),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Login failed');
  }
}
```

## 🗄️ Database

- **Type**: SQLite (db.sqlite3)
- **Location**: `/home/bipul/Bipul/ThopaSichai/ThopaSichai_backend/db.sqlite3`
- **Tables**: User, Token, Admin, Sessions

### Test User Created
- **Username**: farmer1
- **Email**: farmer1@example.com
- **Password**: testpass123
- **Token**: ce0a0d6d69025b72cc5025113cab649149de967b

## 🛠️ Tech Stack

- Django 6.0
- Django REST Framework 3.16.1
- django-cors-headers 4.9.0 (CORS enabled for all origins)
- Token Authentication
- SQLite Database

## 📁 Project Structure

```
ThopaSichai_backend/
├── accounts/                 # Authentication app
│   ├── views.py             # Register, Login, Logout, Profile views
│   ├── serializers.py       # User, Register, Login serializers
│   └── urls.py              # Auth endpoints routing
├── ThopaSichai_backend/     # Project settings
│   ├── settings.py          # CORS, REST Framework config
│   ├── urls.py              # Main URL routing
│   └── asgi.py              # ASGI config (WebSocket ready)
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## ✅ Features Implemented

- ✅ User Registration with validation
- ✅ Email uniqueness check
- ✅ Password confirmation
- ✅ Token-based authentication
- ✅ Login/Logout endpoints
- ✅ User profile retrieval
- ✅ CORS enabled for Flutter
- ✅ Error handling
- ✅ Password hashing (Django default)

## 🔄 Next Steps

1. **Add Device Management API**
   - Create `devices` app
   - Device CRUD operations
   - Link devices to users

2. **Add Sensor Data API**
   - Store sensor readings
   - Historical data retrieval
   - Real-time updates

3. **Add WebSocket Support**
   - Live device status
   - Sensor data streaming
   - Control commands

4. **Connect MQTT Bridge**
   - ESP32 → MQTT → Django
   - Store data in database
   - Broadcast to Flutter app

## 🐛 Troubleshooting

### Can't connect from Flutter app?
1. Make sure server is running: `python manage.py runserver 0.0.0.0:8000`
2. Check your IP: `ip addr show`
3. Ensure firewall allows port 8000
4. Update Flutter app with correct IP address

### Token not working?
- Ensure `Authorization: Token <token>` header is included
- Token format: `Token ce0a0d6d69025b72cc5025113cab649149de967b`
- Space between "Token" and the actual token

## 📊 Testing Results

All endpoints tested and working:
- ✅ Registration creates user and returns token
- ✅ Login validates credentials and returns token
- ✅ Profile requires authentication
- ✅ Wrong password returns 401 error
- ✅ CORS headers present in responses
