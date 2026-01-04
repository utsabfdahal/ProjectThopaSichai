# 📡 ThopaSichai Backend - API Endpoints Reference

## 🌐 Base URL
```
http://10.164.63.195:8000
```

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. Register New User
**Creates a new user account and returns auth token**

**Endpoint**: `POST /api/auth/register/`  
**Authentication**: None (public)  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Test",      // Optional
    "last_name": "User"         // Optional
}
```

**Success Response (201)**:
```json
{
    "token": "abc123def456...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    },
    "message": "Registration successful!"
}
```

**Error Response (400)**:
```json
{
    "username": ["A user with that username already exists."],
    "email": ["A user with this email already exists."],
    "password": ["Password fields didn't match."]
}
```

**Test Command**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

---

### 2. Login
**Authenticate user and get token**

**Endpoint**: `POST /api/auth/login/`  
**Authentication**: None (public)  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "username": "farmer1",
    "password": "testpass123"
}
```

**Success Response (200)**:
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

**Error Response (401)**:
```json
{
    "error": "Invalid username or password"
}
```

**Test Command**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"testpass123"}'
```

---

### 3. Get User Profile
**Get current logged-in user's profile**

**Endpoint**: `GET /api/auth/profile/`  
**Authentication**: Required (Token)  
**Headers**: `Authorization: Token <your-token>`

**Success Response (200)**:
```json
{
    "id": 1,
    "username": "farmer1",
    "email": "farmer1@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Error Response (401)**:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Test Command**:
```bash
curl -X GET http://10.164.63.195:8000/api/auth/profile/ \
  -H "Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b"
```

---

### 4. Logout
**Delete auth token (logout user)**

**Endpoint**: `POST /api/auth/logout/`  
**Authentication**: Required (Token)  
**Headers**: `Authorization: Token <your-token>`

**Success Response (200)**:
```json
{
    "message": "Logout successful!"
}
```

**Test Command**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/logout/ \
  -H "Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b"
```

---

## 🛠️ ADMIN ENDPOINTS

### Django Admin Panel
**Web interface to manage users, tokens, and database**

**URL**: http://10.164.63.195:8000/admin/  
**Username**: `bipul`  
**Password**: (your password)

**What you can do**:
- View all registered users
- Edit user information
- Delete users
- View and manage auth tokens
- See when users were created/last logged in

---

## 📊 HOW TO MONITOR

### 1. See All Users (Command Line)
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python check_users.py
```

### 2. Watch Server Logs
```bash
# In the terminal where Django is running, you'll see:
[24/Dec/2025 06:03:38] "POST /api/auth/login/ HTTP/1.1" 200 123
[24/Dec/2025 06:05:15] "GET /api/auth/profile/ HTTP/1.1" 200 89
```

### 3. Django Shell (Advanced)
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Get all users
users = User.objects.all()
for user in users:
    print(f"{user.username}: {user.email}")

# Get user by username
user = User.objects.get(username='farmer1')
print(user.email)

# Get user's token
token = Token.objects.get(user=user)
print(token.key)

# Count total users
print(f"Total users: {User.objects.count()}")

# Get recently created users (last 7 days)
from datetime import timedelta
from django.utils import timezone
recent = User.objects.filter(
    date_joined__gte=timezone.now() - timedelta(days=7)
)
print(f"Recent users: {recent.count()}")
```

---

## 🔍 MONITORING REAL-TIME

### Check Who Just Logged In
After someone logs in from the Flutter app, run:
```bash
python check_users.py
```

You'll see their:
- Username
- Email
- Token (proves they're logged in)
- Last login time

### View Token Details
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Get all active tokens
tokens = Token.objects.all()
for token in tokens:
    print(f"User: {token.user.username}, Token: {token.key}")

# Verify a specific token
token_key = "ce0a0d6d69025b72cc5025113cab649149de967b"
token = Token.objects.get(key=token_key)
print(f"This token belongs to: {token.user.username}")
```

---

## 🧪 TESTING ENDPOINTS

### Test Registration
```bash
curl -X POST http://10.164.63.195:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2","email":"test2@example.com","password":"pass123","password2":"pass123"}'
```

### Test Login
```bash
curl -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"testpass123"}'
```

### Test With Wrong Password
```bash
curl -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"wrongpassword"}'
```

### Test Profile (Need Token)
```bash
# First login to get token
TOKEN=$(curl -s -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"testpass123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Then use token to get profile
curl -X GET http://10.164.63.195:8000/api/auth/profile/ \
  -H "Authorization: Token $TOKEN"
```

---

## 📱 FROM FLUTTER APP

When your Flutter app makes requests:

### Login Flow
1. User enters username/password
2. App sends POST to `/api/auth/login/`
3. Backend validates credentials
4. Backend returns token + user data
5. App saves token locally (SharedPreferences)
6. App uses token for all future requests

### Authenticated Requests
All requests after login include:
```
Authorization: Token ce0a0d6d69025b72cc5025113cab649149de967b
```

---

## 🎯 CURRENT USERS

Run `python check_users.py` to see:

```
👥 Total Users: 2

🔹 User ID: 1
   Username: farmer1
   Email: farmer1@example.com
   Token: ce0a0d6d69025b72cc5025113cab649149de967b
   Status: Active, Never logged in via app

🔹 User ID: 2
   Username: bipul
   Email: dahalbipul999@gmail.com
   Token: None
   Status: Admin (superuser)
```

---

## 🚀 QUICK COMMANDS

**See all users**:
```bash
python /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend/check_users.py
```

**Access admin panel**:
- Open browser: http://10.164.63.195:8000/admin/
- Login with: bipul / (your password)

**Test login from terminal**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer1","password":"testpass123"}'
```

**Create new test user**:
```bash
curl -X POST http://10.164.63.195:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"testpass123","password2":"testpass123"}'
```
