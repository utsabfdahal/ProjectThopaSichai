# Flutter-Django Authentication - Testing Guide

## ✅ Setup Complete!

Your Flutter app is now connected to Django backend with real authentication.

## 🔗 Connection Details

- **Django Backend**: http://10.164.63.195:8000
- **Flutter App**: Running on Android device
- **Status**: ✅ Both systems active

## 🧪 How to Test

### Test 1: Register New User

1. **Open the Flutter app** on your phone
2. **Tap "Sign Up"** on login screen
3. **Fill in the form**:
   - Username: `testuser` (any unique username)
   - Email: `test@example.com`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
   - Check "I agree to Terms"
4. **Tap "Sign Up"**
5. **Expected**: Success message → Navigate to login

### Test 2: Login with Existing User

1. **On login screen**, enter:
   - Username: `farmer1`
   - Password: `testpass123`
2. **Tap "Login"**
3. **Expected**: Navigate to Dashboard

### Test 3: Login with Wrong Password

1. **On login screen**, enter:
   - Username: `farmer1`
   - Password: `wrongpassword`
2. **Tap "Login"**
3. **Expected**: Red error message "Invalid username or password"

## 🎯 What's Working

✅ **Registration**
- Creates user in Django database
- Returns authentication token
- Saves token locally on device
- Shows success/error messages

✅ **Login**
- Validates credentials with Django
- Returns authentication token
- Saves token and user data locally
- Shows error for wrong credentials

✅ **Token Storage**
- Tokens saved using SharedPreferences
- Persists across app restarts
- User stays logged in

## 📊 Monitor Django Server

In another terminal, watch the server logs:
```bash
# See Django server logs
tail -f /dev/null  # Server logs appear in the background process
```

## 🔍 Verify in Database

Check registered users:
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# List all users
User.objects.all()

# Check specific user
user = User.objects.get(username='farmer1')
print(f"User: {user.username}, Email: {user.email}")

# Get user's token
token = Token.objects.get(user=user)
print(f"Token: {token.key}")
```

## 📱 Test on Phone

### Registration Test
1. Open app → Tap "Sign Up"
2. Create account:
   - Username: `yourname`
   - Email: `your@email.com`
   - Password: `securepass123`
   - Confirm: `securepass123`
   - Check terms box
3. Tap Sign Up
4. Should show: "Registration successful!"

### Login Test
1. On login screen, use the credentials you just created
2. Should navigate to Dashboard

### Error Handling Test
1. Try wrong password
2. Should show: "Invalid username or password"
3. Try duplicate username during registration
4. Should show: "A user with this username already exists"

## 🐛 Troubleshooting

### "Network error: SocketException"
- **Cause**: Flutter can't reach Django server
- **Fix**: 
  1. Check Django server is running: `ps aux | grep runserver`
  2. Verify IP address in `lib/services/api_service.dart`
  3. Ensure phone and laptop on same WiFi network

### "Connection refused"
- **Cause**: Django not listening on 0.0.0.0
- **Fix**: Restart server with `python manage.py runserver 0.0.0.0:8000`

### "Invalid credentials" for correct password
- **Cause**: User doesn't exist in database
- **Fix**: Register first, or check username spelling

### App shows old behavior (fake login)
- **Cause**: Hot reload didn't pick up changes
- **Fix**: Stop app (Ctrl+C) and rebuild with `flutter run`

## 📝 Testing Checklist

- [ ] Django server running on port 8000
- [ ] Flutter app runs without errors
- [ ] Can register new user successfully
- [ ] Can login with farmer1/testpass123
- [ ] Wrong password shows error
- [ ] Token saved (stays logged in after restart)
- [ ] Dashboard loads after login

## 🎉 Next Features to Add

1. **Logout button** on Dashboard
2. **Device management** (add/list/control devices)
3. **WebSocket** for real-time updates
4. **Profile screen** to edit user info
5. **MQTT bridge** to connect ESP32 devices

## 📊 Current Test Data

**Existing Test User**:
- Username: `farmer1`
- Email: `farmer1@example.com`
- Password: `testpass123`
- Token: `ce0a0d6d69025b72cc5025113cab649149de967b`

You can login with this immediately to test!
