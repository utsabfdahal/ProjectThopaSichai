# Complete Guide: Building Android IoT App in 48 Hours
**For: Thopa Sichai Irrigation System | Target: Hackathon Demo**
**Updated: Dec 23, 2025 - Ready for Hackathon Tomorrow!**

---

## ⚡ CURRENT STATUS
- ✅ Flutter Setup Complete
- ✅ Login Screen Done
- ✅ Registration Screen Done
- ✅ Green Theme Applied
- ⏳ Backend (Django) - To be implemented
- ⏳ Dashboard & Device Control - Next priority

---

## Table of Contents
1. [⏰ 48-Hour Action Plan](#48-hour-action-plan-django--flutter)
2. [Django Backend Setup](#django-backend-setup)
3. [Django + WebSocket Integration](#django--websocket-integration)
4. [Connecting Flutter to Django](#connecting-flutter-to-django)
5. [Time Management Strategy](#time-management-strategy)
6. [Flutter Fundamentals](#flutter-fundamentals)
7. [Android Development Essentials](#android-development-essentials)
8. [Backend & API Communication](#backend--api-communication)
9. [WebSockets for Real-Time IoT](#websockets-for-real-time-iot)
10. [Critical Architecture Decisions](#critical-architecture-decisions)
11. [Common Pitfalls & Quick Fixes](#common-pitfalls--quick-fixes)
12. [MVP Features Checklist](#mvp-features-checklist)

---

## ⏰ 48-Hour Action Plan (Django + Flutter)

### **TONIGHT (Before Sleep - 2 hours)**
**Goal: Get basic backend running**

1. **Django Setup (30 mins)**
   ```bash
   pip install django djangorestframework django-cors-headers channels daphne
   django-admin startproject thopa_backend
   cd thopa_backend
   python manage.py startapp devices
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Create Basic API (1 hour)**
   - User authentication endpoint
   - Device list endpoint
   - Simple test with Postman/curl

3. **Test Flutter Connection (30 mins)**
   - Update Flutter app with your local IP
   - Test login API call
   - Verify connection works

### **DAY 1 - HACKATHON START (8-10 hours)**

**Morning (4 hours) - Backend Core**
- [ ] Django REST API for authentication
- [ ] Device CRUD operations
- [ ] WebSocket setup with Channels
- [ ] Test all endpoints

**Afternoon (4 hours) - Flutter Dashboard**
- [ ] Main dashboard screen
- [ ] Device list display
- [ ] Connect to Django API
- [ ] Display device status

**Evening (2 hours) - Integration**
- [ ] WebSocket connection test
- [ ] Real-time device status updates
- [ ] Basic control functionality

### **DAY 2 - HACKATHON (12-14 hours)**

**Morning (4 hours) - Core Features**
- [ ] Device control (ON/OFF)
- [ ] Sensor data display
- [ ] Schedule creation
- [ ] Historical data (if time permits)

**Afternoon (4 hours) - Polish & Testing**
- [ ] Error handling
- [ ] Loading states
- [ ] UI improvements
- [ ] Real device testing

**Evening (4 hours) - Final Sprint**
- [ ] Bug fixes
- [ ] Demo preparation
- [ ] Build release APK
- [ ] Backup plan implementation

### **DAY 3 - FINAL DAY (8-10 hours)**

**Morning (4 hours) - Refinement**
- [ ] UI polish
- [ ] Edge case handling
- [ ] Performance optimization
- [ ] Final testing

**Afternoon (4 hours) - Demo Ready**
- [ ] Create demo script
- [ ] Record demo video (backup)
- [ ] Prepare presentation
- [ ] Test demo flow 3 times

---

## Django Backend Setup

### **1. Quick Django Project Setup**

```bash
# Install dependencies
pip install django djangorestframework django-cors-headers channels daphne python-decouple

# Create project
django-admin startproject thopa_backend
cd thopa_backend
python manage.py startapp devices
python manage.py startapp accounts
```

### **2. Essential Django Settings**

**File: `thopa_backend/settings.py`**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    
    # Your apps
    'devices',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS Settings (for Flutter to connect)
CORS_ALLOW_ALL_ORIGINS = True  # For development only!
# For production:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://your-app.com",
# ]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Channels (WebSocket)
ASGI_APPLICATION = 'thopa_backend.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # Use Redis in production
    },
}
```

### **3. Create Device Model**

**File: `devices/models.py`**
```python
from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    DEVICE_TYPES = [
        ('PUMP', 'Water Pump'),
        ('VALVE', 'Irrigation Valve'),
        ('SENSOR', 'Sensor Module'),
    ]
    
    STATUS_CHOICES = [
        ('ON', 'On'),
        ('OFF', 'Off'),
        ('ERROR', 'Error'),
    ]
    
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=50, unique=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OFF')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.device_id})"

class SensorReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    soil_moisture = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"

class Schedule(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='schedules')
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    is_active = models.BooleanField(default=True)
    days_of_week = models.CharField(max_length=50)  # e.g., "1,2,3,4,5" for weekdays
    
    def __str__(self):
        return f"{self.device.name} - {self.start_time}"
```

### **4. Create API Serializers**

**File: `devices/serializers.py`**
```python
from rest_framework import serializers
from .models import Device, SensorReading, Schedule

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'device_id', 'device_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ['id', 'device', 'soil_moisture', 'temperature', 'humidity', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'device', 'start_time', 'duration_minutes', 'is_active', 'days_of_week']
```

### **5. Create API Views**

**File: `devices/views.py`**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device, SensorReading, Schedule
from .serializers import DeviceSerializer, SensorReadingSerializer, ScheduleSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Device.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        """Control device ON/OFF"""
        device = self.get_object()
        action_cmd = request.data.get('action', '').upper()
        
        if action_cmd in ['ON', 'OFF']:
            device.status = action_cmd
            device.save()
            
            # TODO: Send command to ESP32 via MQTT
            # mqtt_client.publish(f'device/{device.device_id}/control', action_cmd)
            
            return Response({
                'status': 'success',
                'device_id': device.device_id,
                'new_status': device.status
            })
        
        return Response(
            {'error': 'Invalid action. Use ON or OFF'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get sensor readings for a device"""
        device = self.get_object()
        readings = device.readings.all()[:50]  # Last 50 readings
        serializer = SensorReadingSerializer(readings, many=True)
        return Response(serializer.data)

class SensorReadingViewSet(viewsets.ModelViewSet):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SensorReading.objects.filter(device__owner=self.request.user)

class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Schedule.objects.filter(device__owner=self.request.user)
```

### **6. Setup URLs**

**File: `devices/urls.py`**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, SensorReadingViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'readings', SensorReadingViewSet, basename='reading')
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]
```

**File: `thopa_backend/urls.py`**
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', obtain_auth_token, name='api_login'),
    path('api/', include('devices.urls')),
]
```

### **7. Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

---

## Django + WebSocket Integration

### **1. Setup Channels for WebSocket**

**File: `thopa_backend/asgi.py`**
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from devices.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thopa_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### **2. Create WebSocket Consumer**

**File: `devices/consumers.py`**
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Device

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'devices'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to device updates'
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'control':
            # Handle device control
            device_id = data.get('device_id')
            action = data.get('action')
            
            # Update device status
            await self.update_device_status(device_id, action)
            
            # Broadcast to all clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'device_status',
                    'device_id': device_id,
                    'status': action,
                }
            )
    
    async def device_status(self, event):
        """Send device status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'device_status',
            'device_id': event['device_id'],
            'status': event['status'],
        }))
    
    async def sensor_data(self, event):
        """Send sensor data to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'sensor_data',
            'device_id': event['device_id'],
            'soil_moisture': event.get('soil_moisture'),
            'temperature': event.get('temperature'),
            'humidity': event.get('humidity'),
            'timestamp': event.get('timestamp'),
        }))
    
    @database_sync_to_async
    def update_device_status(self, device_id, status):
        try:
            device = Device.objects.get(device_id=device_id)
            device.status = status
            device.save()
            return True
        except Device.DoesNotExist:
            return False
```

### **3. Setup WebSocket Routing**

**File: `devices/routing.py`**
```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/devices/$', consumers.DeviceConsumer.as_asgi()),
]
```

### **4. Run with Daphne (ASGI Server)**

```bash
# Install daphne
pip install daphne

# Run server
daphne -b 0.0.0.0 -p 8000 thopa_backend.asgi:application
```

---

## Connecting Flutter to Django

### **1. Add Required Packages**

**File: `pubspec.yaml`**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  web_socket_channel: ^2.4.0
  shared_preferences: ^2.2.2
  provider: ^6.1.1
```

### **2. Create Django API Service**

**File: `lib/services/django_api_service.dart`**
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class DjangoApiService {
  // Change this to your computer's IP address
  static const String baseUrl = 'http://192.168.1.100:8000/api';
  
  String? _token;
  
  // Login
  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['token'];
        
        // Save token
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);
        
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }
  
  // Get devices
  Future<List<Map<String, dynamic>>> getDevices() async {
    await _loadToken();
    
    final response = await http.get(
      Uri.parse('$baseUrl/devices/'),
      headers: {
        'Authorization': 'Token $_token',
      },
    );
    
    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    }
    throw Exception('Failed to load devices');
  }
  
  // Control device
  Future<bool> controlDevice(int deviceId, String action) async {
    await _loadToken();
    
    final response = await http.post(
      Uri.parse('$baseUrl/devices/$deviceId/control/'),
      headers: {
        'Authorization': 'Token $_token',
        'Content-Type': 'application/json',
      },
      body: json.encode({'action': action}),
    );
    
    return response.statusCode == 200;
  }
  
  // Get sensor readings
  Future<List<Map<String, dynamic>>> getSensorReadings(int deviceId) async {
    await _loadToken();
    
    final response = await http.get(
      Uri.parse('$baseUrl/devices/$deviceId/readings/'),
      headers: {
        'Authorization': 'Token $_token',
      },
    );
    
    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    }
    throw Exception('Failed to load readings');
  }
  
  Future<void> _loadToken() async {
    if (_token == null) {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('auth_token');
    }
  }
}
```

### **3. Create WebSocket Service for Django**

**File: `lib/services/django_websocket_service.dart`**
```dart
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class DjangoWebSocketService {
  // Change this to your computer's IP address
  static const String wsUrl = 'ws://192.168.1.100:8000/ws/devices/';
  
  WebSocketChannel? _channel;
  
  Function(Map<String, dynamic>)? onSensorData;
  Function(String deviceId, String status)? onDeviceStatus;
  Function(String)? onError;
  
  void connect() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (message) {
          final data = json.decode(message);
          _handleMessage(data);
        },
        onError: (error) {
          print('WebSocket error: $error');
          onError?.call(error.toString());
          _reconnect();
        },
        onDone: () {
          print('WebSocket closed');
          _reconnect();
        },
      );
      
      print('WebSocket connected to Django');
    } catch (e) {
      print('Connection failed: $e');
      onError?.call(e.toString());
    }
  }
  
  void _handleMessage(Map<String, dynamic> data) {
    final type = data['type'];
    
    switch (type) {
      case 'sensor_data':
        onSensorData?.call(data);
        break;
      case 'device_status':
        onDeviceStatus?.call(data['device_id'], data['status']);
        break;
      case 'connection':
        print('Connected: ${data['message']}');
        break;
    }
  }
  
  void sendControl(String deviceId, String action) {
    if (_channel != null) {
      final message = json.encode({
        'type': 'control',
        'device_id': deviceId,
        'action': action,
      });
      _channel!.sink.add(message);
    }
  }
  
  void _reconnect() {
    Future.delayed(Duration(seconds: 5), () {
      connect();
    });
  }
  
  void disconnect() {
    _channel?.sink.close();
  }
}
```

### **4. Update Login Screen to Use Django**

**File: `lib/screens/login_screen.dart`** (Update the `_handleLogin` method)
```dart
import '../services/django_api_service.dart';

// Inside _LoginScreenState class:
final _apiService = DjangoApiService();

Future<void> _handleLogin() async {
  if (_formKey.currentState!.validate()) {
    setState(() {
      _isLoading = true;
    });

    final success = await _apiService.login(
      _emailController.text,
      _passwordController.text,
    );

    setState(() {
      _isLoading = false;
    });

    if (mounted) {
      if (success) {
        // Navigate to dashboard
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => DashboardScreen()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Login failed. Check your credentials.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
```

---

## 🎯 YOUR IMMEDIATE NEXT STEPS

### **RIGHT NOW (Tonight):**

1. **Set up Django backend (30 mins)**
   ```bash
   cd ~/Bipul/ThopaSichai
   mkdir backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install django djangorestframework django-cors-headers channels
   ```

2. **Create basic Django project (30 mins)**
   - Follow steps in "Django Backend Setup" section
   - Run migrations
   - Create a test user

3. **Update Flutter with your IP (15 mins)**
   ```bash
   # Find your IP
   ip addr show | grep inet
   # or
   hostname -I
   ```
   - Update `baseUrl` in Django services with your IP
   - Test connection

4. **Quick test (15 mins)**
   - Run Django server
   - Try login from Flutter app
   - Verify it works

### **Tomorrow Morning (Start of Hackathon):**
1. Create Dashboard screen
2. Connect device list
3. Implement WebSocket
4. Test real-time updates

---

---

## Time Management Strategy

### **Hour-by-Hour Breakdown (56 hours total)**

**TODAY (8 hours remaining):**
- ✅ Hour 1-2: Flutter setup (DONE!)
- ⏳ Hour 3-4: Project structure + UI mockups
- ⏳ Hour 5-6: Basic UI screens (Login, Dashboard)
- ⏳ Hour 7-8: WebSocket connection testing

**DAY 2 (24 hours):**
- Morning (4h): Core device control functionality
- Afternoon (4h): Real-time sensor data display
- Evening (4h): Scheduling/automation UI
- Night (4h): ESP32 integration testing
- Buffer (8h): Bug fixes, polish

**DAY 3 (24 hours):**
- Morning (8h): Final features, edge cases
- Afternoon (8h): UI polish, user testing
- Evening (8h): Demo preparation, backup plans

### **Priority Matrix (What to Focus On)**

**Must Have (P0):**
- Basic device ON/OFF control
- Real-time sensor readings
- Connection status indicator
- Simple scheduling

**Should Have (P1):**
- Authentication
- Multiple device support
- Historical data charts
- Notifications

**Nice to Have (P2):**
- Advanced scheduling
- Weather integration
- User profiles
- Analytics

---

## Flutter Fundamentals

### **What is Flutter?**
Flutter is Google's UI framework that lets you build apps for Android, iOS, web, and desktop from a **single codebase**. It uses the Dart programming language.

### **Key Concepts You MUST Know**

#### 1. **Everything is a Widget**
Flutter builds UIs by composing widgets (like building blocks):

```dart
// Simple widget example
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('My IoT App')),
        body: Center(child: Text('Hello World')),
      ),
    );
  }
}
```

#### 2. **Stateless vs Stateful Widgets**

**StatelessWidget:** Doesn't change after built (static UI)
```dart
class WelcomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Text('Welcome!'); // Never changes
  }
}
```

**StatefulWidget:** Can change over time (dynamic UI)
```dart
class DeviceStatus extends StatefulWidget {
  @override
  _DeviceStatusState createState() => _DeviceStatusState();
}

class _DeviceStatusState extends State<DeviceStatus> {
  bool isOn = false;
  
  void toggleDevice() {
    setState(() {
      isOn = !isOn; // UI rebuilds when state changes
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Switch(
      value: isOn,
      onChanged: (value) => toggleDevice(),
    );
  }
}
```

#### 3. **Hot Reload - Your Best Friend**
- Make changes to code
- Press **'r'** in terminal
- See changes in **< 1 second** (no rebuild!)
- Press **'R'** for full restart

#### 4. **Common Widgets You'll Use**

```dart
// Layout Widgets
Column(children: [widget1, widget2])  // Vertical stack
Row(children: [widget1, widget2])     // Horizontal row
Container()                           // Box with padding/margin
ListView()                            // Scrollable list
GridView()                            // Grid layout

// Input Widgets
TextField()                           // Text input
Switch()                              // Toggle switch
Slider()                              // Value slider
ElevatedButton()                      // Button

// Display Widgets
Text()                                // Display text
Image()                               // Display image
Icon()                                // Display icon
Card()                                // Material card
```

#### 5. **Navigation Between Screens**

```dart
// Navigate to new screen
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => DeviceDetailScreen()),
);

// Go back
Navigator.pop(context);
```

#### 6. **State Management Basics**

For your hackathon, use **Provider** (simple and effective):

```dart
// 1. Create a model
class DeviceModel extends ChangeNotifier {
  bool _isOn = false;
  
  bool get isOn => _isOn;
  
  void toggle() {
    _isOn = !_isOn;
    notifyListeners(); // Updates all listening widgets
  }
}

// 2. Provide it at the top
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => DeviceModel(),
      child: MyApp(),
    ),
  );
}

// 3. Use it in widgets
class ControlButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final device = Provider.of<DeviceModel>(context);
    
    return Switch(
      value: device.isOn,
      onChanged: (value) => device.toggle(),
    );
  }
}
```

### **Flutter Project Structure**

```
thopa_sichai_app/
├── lib/
│   ├── main.dart              # Entry point
│   ├── screens/               # UI screens
│   │   ├── login_screen.dart
│   │   ├── dashboard_screen.dart
│   │   └── device_detail_screen.dart
│   ├── widgets/               # Reusable UI components
│   │   ├── device_card.dart
│   │   └── sensor_gauge.dart
│   ├── models/                # Data models
│   │   └── device.dart
│   ├── services/              # Business logic
│   │   ├── websocket_service.dart
│   │   └── api_service.dart
│   └── utils/                 # Helpers
│       └── constants.dart
├── pubspec.yaml               # Dependencies
└── android/                   # Android specific config
```

---

## Android Development Essentials

### **What You Need to Know (The Minimum)**

#### 1. **Android Permissions**
Your IoT app needs internet access. Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Add these permissions -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    
    <application
        android:label="Thopa Sichai"
        android:icon="@mipmap/ic_launcher">
        <!-- Your app config -->
    </application>
</manifest>
```

#### 2. **App Configuration**
Edit `android/app/build.gradle`:

```gradle
android {
    defaultConfig {
        applicationId "com.thoparichai.thopa_sichai_app"
        minSdkVersion 21     // Supports Android 5.0+
        targetSdkVersion 33  // Latest stable
    }
}
```

#### 3. **Debug vs Release Builds**

```bash
# Debug (for development)
flutter run

# Release (for submission/demo)
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

#### 4. **Testing on Real Device**
- Always test on your physical phone
- Emulator ≠ Real device (especially for sensors/network)
- Check different screen sizes if possible

#### 5. **Android Lifecycle**
Flutter handles most of this, but know:
- App goes to background → WebSocket may disconnect
- App returns → Reconnect WebSocket
- Use `AppLifecycleState` to detect this

```dart
class _MyAppState extends State<MyApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }
  
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // App came back - reconnect WebSocket
      webSocketService.reconnect();
    }
  }
}
```

---

## Backend & API Communication

### **HTTP vs WebSocket - When to Use What**

**HTTP/REST API (Request-Response):**
- User authentication (login)
- Fetch device list
- Update settings
- Get historical data

**WebSocket (Real-Time):**
- Live sensor readings
- Device ON/OFF status
- Real-time control commands
- Instant notifications

### **HTTP Requests in Flutter**

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'https://your-server.com/api';
  
  // Login
  Future<bool> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      // Save token
      return true;
    }
    return false;
  }
  
  // Get devices
  Future<List<Device>> getDevices() async {
    final response = await http.get(
      Uri.parse('$baseUrl/devices'),
      headers: {'Authorization': 'Bearer YOUR_TOKEN'},
    );
    
    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.map((json) => Device.fromJson(json)).toList();
    }
    throw Exception('Failed to load devices');
  }
  
  // Control device
  Future<void> controlDevice(String deviceId, bool turnOn) async {
    await http.post(
      Uri.parse('$baseUrl/devices/$deviceId/control'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN',
      },
      body: json.encode({'action': turnOn ? 'ON' : 'OFF'}),
    );
  }
}
```

### **Error Handling**

```dart
try {
  final devices = await apiService.getDevices();
  setState(() {
    this.devices = devices;
  });
} catch (e) {
  // Show error to user
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Failed to load devices: $e')),
  );
}
```

---

## WebSockets for Real-Time IoT

### **Why WebSockets for IoT?**
- **Real-time:** Instant updates when sensor changes
- **Bidirectional:** Server can push data anytime
- **Efficient:** Single connection, less overhead
- **Perfect for:** Live monitoring, instant control

### **WebSocket Architecture for Your Project**

```
ESP32 → MQTT Broker → Server (WebSocket Bridge) → Flutter App
                                                   ↓
                                          Live sensor data
                                          Device control
```

### **Implementing WebSocket in Flutter**

**Install package:**
```yaml
# pubspec.yaml
dependencies:
  web_socket_channel: ^2.4.0
```

**Create WebSocket Service:**

```dart
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class WebSocketService {
  WebSocketChannel? _channel;
  final String serverUrl = 'ws://your-server.com:8080/ws';
  
  // Callbacks for different message types
  Function(Map<String, dynamic>)? onSensorData;
  Function(bool)? onDeviceStatus;
  Function(String)? onError;
  
  // Connect to WebSocket
  void connect() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(serverUrl));
      
      // Listen for messages
      _channel!.stream.listen(
        (message) {
          final data = json.decode(message);
          handleMessage(data);
        },
        onError: (error) {
          print('WebSocket error: $error');
          onError?.call(error.toString());
          reconnect();
        },
        onDone: () {
          print('WebSocket closed');
          reconnect();
        },
      );
      
      print('WebSocket connected');
    } catch (e) {
      print('Connection failed: $e');
      onError?.call(e.toString());
    }
  }
  
  // Handle incoming messages
  void handleMessage(Map<String, dynamic> data) {
    final type = data['type'];
    
    switch (type) {
      case 'sensor_data':
        onSensorData?.call(data);
        break;
      case 'device_status':
        onDeviceStatus?.call(data['status'] == 'ON');
        break;
      default:
        print('Unknown message type: $type');
    }
  }
  
  // Send control command
  void sendCommand(String deviceId, String action) {
    if (_channel != null) {
      final message = json.encode({
        'type': 'control',
        'device_id': deviceId,
        'action': action,
      });
      _channel!.sink.add(message);
    }
  }
  
  // Reconnect logic
  void reconnect() {
    Future.delayed(Duration(seconds: 5), () {
      connect();
    });
  }
  
  // Disconnect
  void disconnect() {
    _channel?.sink.close();
  }
}
```

### **Using WebSocket in Your UI**

```dart
class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final WebSocketService ws = WebSocketService();
  double soilMoisture = 0;
  bool deviceOn = false;
  
  @override
  void initState() {
    super.initState();
    
    // Set up callbacks
    ws.onSensorData = (data) {
      setState(() {
        soilMoisture = data['soil_moisture'];
      });
    };
    
    ws.onDeviceStatus = (status) {
      setState(() {
        deviceOn = status;
      });
    };
    
    ws.onError = (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Connection error: $error')),
      );
    };
    
    // Connect
    ws.connect();
  }
  
  @override
  void dispose() {
    ws.disconnect();
    super.dispose();
  }
  
  void toggleDevice() {
    ws.sendCommand('device_1', deviceOn ? 'OFF' : 'ON');
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Dashboard')),
      body: Column(
        children: [
          Text('Soil Moisture: ${soilMoisture.toStringAsFixed(1)}%'),
          Switch(
            value: deviceOn,
            onChanged: (value) => toggleDevice(),
          ),
        ],
      ),
    );
  }
}
```

### **Message Protocol (What Your Server Should Send)**

```json
// Sensor data
{
  "type": "sensor_data",
  "device_id": "esp32_001",
  "timestamp": 1703345678,
  "soil_moisture": 45.2,
  "temperature": 28.5,
  "humidity": 65.0
}

// Device status
{
  "type": "device_status",
  "device_id": "esp32_001",
  "status": "ON",
  "timestamp": 1703345678
}

// Control command (app → server)
{
  "type": "control",
  "device_id": "esp32_001",
  "action": "ON"
}
```

---

## Critical Architecture Decisions

### **1. State Management: Provider vs Others**

**For 56-hour hackathon → Use Provider**
- ✅ Simple to learn (30 minutes)
- ✅ Adequate for your app size
- ✅ Official Flutter recommendation
- ❌ Don't use: Bloc, Redux, Riverpod (overkill for hackathon)

### **2. Backend Architecture**

**Recommended for IoT:**
```
ESP32 (MQTT) → Mosquitto Broker → Python/Node Backend → WebSocket Server → Flutter App
                                         ↓
                                   PostgreSQL/MongoDB
                                   (Store history)
```

**Simple Backend (Python FastAPI example):**
```python
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

# Store active WebSocket connections
connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    
    try:
        while True:
            # Receive from Flutter app
            data = await websocket.receive_json()
            
            # Forward to ESP32 (via MQTT or direct)
            await handle_control_command(data)
            
    except:
        connections.remove(websocket)

# Broadcast sensor data to all connected apps
async def broadcast_sensor_data(data):
    for connection in connections:
        await connection.send_json(data)
```

### **3. Data Storage**

**Local (App):**
- Use `shared_preferences` for settings
- Use `sqflite` if you need local database

```dart
// Save settings locally
import 'package:shared_preferences/shared_preferences.dart';

Future<void> saveToken(String token) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString('auth_token', token);
}
```

**Remote (Server):**
- PostgreSQL for structured data (users, devices)
- InfluxDB/TimescaleDB for time-series (sensor readings)

### **4. Authentication Strategy**

**Simple JWT approach:**
1. User logs in → Server returns JWT token
2. App stores token locally
3. Include token in all API requests
4. WebSocket: Send token on connect

```dart
// Add token to HTTP headers
headers: {
  'Authorization': 'Bearer $token',
}

// Send token via WebSocket
ws.sendMessage({
  'type': 'auth',
  'token': token,
});
```

---

## Common Pitfalls & Quick Fixes

### **Problem 1: WebSocket Keeps Disconnecting**
**Cause:** Network changes, server timeout, app backgrounded

**Solution:**
```dart
// Auto-reconnect logic
void reconnect() {
  if (_reconnecting) return;
  _reconnecting = true;
  
  Future.delayed(Duration(seconds: 5), () {
    _reconnecting = false;
    connect();
  });
}

// Heartbeat to keep connection alive
void startHeartbeat() {
  Timer.periodic(Duration(seconds: 30), (timer) {
    if (_channel != null) {
      _channel!.sink.add(json.encode({'type': 'ping'}));
    }
  });
}
```

### **Problem 2: UI Freezes During Network Calls**
**Cause:** Blocking UI thread

**Solution:** Use async/await properly
```dart
// ❌ Wrong (blocks UI)
final data = getDataFromServer();

// ✅ Correct (async)
final data = await getDataFromServer();
setState(() {
  this.data = data;
});
```

### **Problem 3: setState Called After Widget Disposed**
**Cause:** Async operation completes after widget is removed

**Solution:**
```dart
@override
void dispose() {
  _isDisposed = true;
  super.dispose();
}

Future<void> loadData() async {
  final data = await fetchData();
  if (!_isDisposed) {
    setState(() {
      this.data = data;
    });
  }
}
```

### **Problem 4: App Crashes on Real Device but Works on Web**
**Causes:**
- Missing Android permissions
- Network security config
- Platform-specific code

**Solution:**
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="true">  <!-- For HTTP (dev only) -->
</application>
```

### **Problem 5: Hot Reload Doesn't Update UI**
**Cause:** State not properly managed

**Solution:** Press 'R' for hot restart (full rebuild)

---

## MVP Features Checklist

### **Day 1 - Core Functionality (8 hours)**
- [ ] Login screen (hardcoded credentials OK)
- [ ] Dashboard with device list
- [ ] WebSocket connection established
- [ ] Display live sensor reading (at least one)
- [ ] Device ON/OFF button (functional)

### **Day 2 - Essential Features (24 hours)**
- [ ] Real-time sensor data (soil moisture, temp)
- [ ] Historical data chart (simple line graph)
- [ ] Schedule creation (time-based watering)
- [ ] Manual override control
- [ ] Connection status indicator
- [ ] Error handling & user feedback
- [ ] Multiple device support

### **Day 3 - Polish & Demo Prep (24 hours)**
- [ ] Splash screen
- [ ] App icon
- [ ] Loading states
- [ ] Empty states (no devices)
- [ ] Settings screen
- [ ] Build release APK
- [ ] Test on real device thoroughly
- [ ] Prepare demo script

---

## Quick Reference: Essential Packages

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  provider: ^6.1.1
  
  # HTTP & WebSocket
  http: ^1.1.0
  web_socket_channel: ^2.4.0
  
  # Charts
  fl_chart: ^0.65.0
  
  # Storage
  shared_preferences: ^2.2.2
  
  # UI
  google_fonts: ^6.1.0
  
  # Utils
  intl: ^0.18.1  # Date formatting
```

---

## Development Speed Tips

### **1. Use Snippets**
Create code snippets for common patterns:
- StatefulWidget boilerplate
- Provider setup
- API call template

### **2. Copy-Paste Smartly**
- Material Design Gallery: material.io
- Flutter Widget Catalog: docs.flutter.dev/ui/widgets
- GitHub: Search for similar projects

### **3. Debug Efficiently**
```dart
// Print debugging
print('Value: $value');

// Debug widget tree
debugPrint('Widget built');

// Performance profiling
Timeline.startSync('fetchData');
await fetchData();
Timeline.finishSync();
```

### **4. Test on Web First**
- Faster iteration
- Easier debugging (browser DevTools)
- Switch to phone for final testing

---

## Emergency Backup Plans

**If WebSocket fails:**
- Fall back to HTTP polling (every 2 seconds)
- Still functional, just less "real-time"

**If server isn't ready:**
- Use mock data in the app
- Demo with simulated sensor values
- Show UI/UX capabilities

**If time runs out:**
- Focus on demo flow (hardcode if needed)
- Prioritize what judges see
- Good presentation > perfect code

---

## Final Advice

### **Do:**
- ✅ Keep it simple
- ✅ Test frequently on real device
- ✅ Commit code regularly
- ✅ Sleep at least 4-5 hours per night
- ✅ Ask for help when stuck (don't waste hours)

### **Don't:**
- ❌ Over-engineer
- ❌ Perfect every detail
- ❌ Add features not in MVP
- ❌ Skip error handling
- ❌ Forget to build release APK

### **Remember:**
> "A working demo with 5 features beats a broken app with 20 features."

---

## Quick Start Command Reference

```bash
# Create new screen
touch lib/screens/device_screen.dart

# Add package
flutter pub add package_name

# Run on phone
flutter run

# Build APK
flutter build apk --release

# Clean build (if issues)
flutter clean
flutter pub get
flutter run

# Check devices
flutter devices

# Hot reload: Press 'r'
# Hot restart: Press 'R'
```

---

## You've Got This! 🚀

You have:
- ✅ Flutter working
- ✅ Android deployment ready
- ✅ 56 hours
- ✅ This guide

**Next Steps:**
1. Read this guide (30 mins)
2. Sketch your app screens (30 mins)
3. Start coding the dashboard (2 hours)
4. Test WebSocket connection (2 hours)
5. Build features iteratively

**Need Help?**
- Flutter docs: docs.flutter.dev
- Stack Overflow
- Flutter Discord/Reddit
- Me! (Claude)

Good luck with your hackathon! 🌱💧
