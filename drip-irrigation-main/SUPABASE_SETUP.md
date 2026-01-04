# Supabase Local Setup Guide - Smart Drip Irrigation System

## 🎯 Overview

Run Supabase locally on your laptop (192.168.1.100) to provide:
- **PostgreSQL Database** for storing sensor data, schedules, user accounts
- **REST API** for mobile app communication
- **Real-time subscriptions** for live dashboard updates
- **Authentication** for user login/signup
- **Storage** for images, logs, reports

---

## 📋 Prerequisites

- **Laptop/PC** running Ubuntu/Linux (your main server)
- **Docker** and **Docker Compose** installed
- **8 GB RAM minimum** (16 GB recommended)
- **10 GB free disk space**
- Connected to same router as ESP32

---

## 🔧 Part 1: Install Docker & Docker Compose

### Step 1.1: Install Docker
```bash
# Update packages
sudo apt update

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Apply group changes (logout/login or run)
newgrp docker

# Verify installation
docker --version
```

### Step 1.2: Install Docker Compose
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

---

## 🚀 Part 2: Install Supabase Locally

### Step 2.1: Clone Supabase Repository
```bash
# Go to your project directory
cd /home/krishna/Projects/drip-irrigation

# Clone Supabase
git clone --depth 1 https://github.com/supabase/supabase
cd supabase/docker

# Copy example env file
cp .env.example .env
```

### Step 2.2: Configure Supabase
Edit the `.env` file:
```bash
nano .env
```

**Key configurations to change:**
```bash
############
# Secrets
############
# Change these to secure random strings
POSTGRES_PASSWORD=your_super_secret_postgres_password
JWT_SECRET=your_super_secret_jwt_token_with_at_least_32_characters
ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE
SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q

############
# Dashboard
############
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_dashboard_password

############
# Database
############
POSTGRES_HOST=db
POSTGRES_DB=postgres
POSTGRES_PORT=5432

############
# API
############
# This will be accessible at http://192.168.1.100:8000
KONG_HTTP_PORT=8000
KONG_HTTPS_PORT=8443

############
# Studio (Dashboard)
############
# Accessible at http://192.168.1.100:3000
STUDIO_PORT=3000

############
# Auth
############
SITE_URL=http://192.168.1.100:3000
ADDITIONAL_REDIRECT_URLS=
JWT_EXPIRY=3600
DISABLE_SIGNUP=false
```

### Step 2.3: Start Supabase
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs (if needed)
docker-compose logs -f
```

**Wait 2-3 minutes** for all services to start.

### Step 2.4: Access Supabase Dashboard
Open browser: **http://192.168.1.100:3000**

Login with:
- Username: `admin` (from .env)
- Password: `your_dashboard_password` (from .env)

---

## 💾 Part 3: Create Database Schema

### Step 3.1: Access SQL Editor
In Supabase Dashboard:
1. Go to **SQL Editor** (left sidebar)
2. Click **New Query**

### Step 3.2: Create Tables
```sql
-- Create devices table
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id TEXT UNIQUE NOT NULL,
  device_name TEXT NOT NULL,
  device_type TEXT NOT NULL, -- 'test_node', 'zone_controller'
  zone_number INTEGER,
  location TEXT,
  is_active BOOLEAN DEFAULT true,
  last_seen TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sensor_data table
CREATE TABLE sensor_data (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  soil_moisture_1 NUMERIC(5,2),
  soil_moisture_2 NUMERIC(5,2),
  soil_moisture_3 NUMERIC(5,2),
  soil_moisture_4 NUMERIC(5,2),
  tank_level NUMERIC(5,2),
  temperature NUMERIC(5,2),
  humidity NUMERIC(5,2),
  flow_rate NUMERIC(6,2),
  battery_voltage NUMERIC(4,2),
  wifi_rssi INTEGER
);

-- Create irrigation_events table
CREATE TABLE irrigation_events (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  zone_number INTEGER NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE,
  duration_seconds INTEGER,
  water_used_liters NUMERIC(8,2),
  trigger_type TEXT, -- 'manual', 'scheduled', 'sensor', 'automatic'
  status TEXT DEFAULT 'running', -- 'running', 'completed', 'stopped', 'error'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create schedules table
CREATE TABLE schedules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  zone_number INTEGER NOT NULL,
  name TEXT NOT NULL,
  enabled BOOLEAN DEFAULT true,
  start_time TIME NOT NULL,
  duration_minutes INTEGER NOT NULL,
  days_of_week INTEGER[], -- [0,1,2,3,4,5,6] for Sun-Sat
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create alerts table
CREATE TABLE alerts (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  alert_type TEXT NOT NULL, -- 'low_battery', 'low_water', 'sensor_error', 'offline'
  severity TEXT NOT NULL, -- 'info', 'warning', 'critical'
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create system_logs table
CREATE TABLE system_logs (
  id BIGSERIAL PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  log_level TEXT NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR'
  message TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_sensor_data_device_time ON sensor_data(device_id, timestamp DESC);
CREATE INDEX idx_irrigation_events_device ON irrigation_events(device_id, start_time DESC);
CREATE INDEX idx_alerts_device_unread ON alerts(device_id, is_read);
CREATE INDEX idx_system_logs_device_time ON system_logs(device_id, created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE irrigation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now, restrict later)
CREATE POLICY "Enable all for authenticated users" ON devices
  FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON sensor_data
  FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON irrigation_events
  FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON schedules
  FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON alerts
  FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON system_logs
  FOR ALL USING (true);

-- Insert test device
INSERT INTO devices (device_id, device_name, device_type, zone_number, location)
VALUES ('smartkisan_test', 'Test Node', 'test_node', 0, 'Development Lab');
```

Click **RUN** to execute.

---

## 🔌 Part 4: Integrate with MQTT Server

### Step 4.1: Create MQTT to Supabase Bridge
```bash
cd /home/krishna/Projects/drip-irrigation/server
nano mqtt_supabase_bridge.py
```

Add this code:
```python
"""
MQTT to Supabase Bridge
Listens to MQTT messages and stores them in Supabase
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime
from supabase import create_client, Client
import os

# Supabase configuration
SUPABASE_URL = "http://192.168.1.100:8000"  # Your laptop IP
SUPABASE_KEY = "YOUR_ANON_KEY_FROM_ENV_FILE"  # Get from .env

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe("irrigation/#")

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        print(f"Received: {topic}")
        
        # Parse topic: irrigation/{device_id}/{message_type}
        parts = topic.split('/')
        if len(parts) < 3:
            return
        
        device_id = parts[1]
        message_type = parts[2]
        
        # Store in Supabase based on message type
        if message_type == "sensors":
            store_sensor_data(device_id, payload)
        elif message_type == "status":
            update_device_status(device_id, payload)
        elif message_type == "heartbeat":
            update_device_heartbeat(device_id, payload)
        elif message_type == "telemetry":
            store_telemetry(device_id, payload)
            
    except Exception as e:
        print(f"Error processing message: {e}")

def store_sensor_data(device_id, data):
    """Store sensor data in database"""
    try:
        sensors = data.get('sensors', {})
        soil_moisture = sensors.get('soil_moisture', [0, 0, 0, 0])
        
        record = {
            'device_id': device_id,
            'soil_moisture_1': soil_moisture[0] if len(soil_moisture) > 0 else None,
            'soil_moisture_2': soil_moisture[1] if len(soil_moisture) > 1 else None,
            'soil_moisture_3': soil_moisture[2] if len(soil_moisture) > 2 else None,
            'soil_moisture_4': soil_moisture[3] if len(soil_moisture) > 3 else None,
            'tank_level': sensors.get('tank_level'),
            'temperature': sensors.get('temperature'),
            'humidity': sensors.get('humidity'),
            'flow_rate': sensors.get('flow_rate'),
            'wifi_rssi': data.get('wifi_rssi')
        }
        
        result = supabase.table('sensor_data').insert(record).execute()
        print(f"✅ Stored sensor data for {device_id}")
        
    except Exception as e:
        print(f"❌ Error storing sensor data: {e}")

def update_device_status(device_id, data):
    """Update device status"""
    try:
        status = data.get('status')
        
        # Update last_seen timestamp
        result = supabase.table('devices').update({
            'last_seen': datetime.now().isoformat(),
            'is_active': status == 'online'
        }).eq('device_id', device_id).execute()
        
        print(f"✅ Updated status for {device_id}: {status}")
        
    except Exception as e:
        print(f"❌ Error updating status: {e}")

def update_device_heartbeat(device_id, data):
    """Update device heartbeat"""
    try:
        result = supabase.table('devices').update({
            'last_seen': datetime.now().isoformat()
        }).eq('device_id', device_id).execute()
        
        # Log heartbeat
        supabase.table('system_logs').insert({
            'device_id': device_id,
            'log_level': 'INFO',
            'message': 'Heartbeat received',
            'metadata': data
        }).execute()
        
    except Exception as e:
        print(f"❌ Error updating heartbeat: {e}")

def store_telemetry(device_id, data):
    """Store complete telemetry data"""
    try:
        # Store as system log with full data
        result = supabase.table('system_logs').insert({
            'device_id': device_id,
            'log_level': 'INFO',
            'message': 'Telemetry data',
            'metadata': data
        }).execute()
        
        print(f"✅ Stored telemetry for {device_id}")
        
    except Exception as e:
        print(f"❌ Error storing telemetry: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("🌱 MQTT to Supabase Bridge Starting...")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Supabase URL: {SUPABASE_URL}")
    print("=" * 60)
    
    # Create MQTT client
    client = mqtt.Client(client_id="supabase_bridge")
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to MQTT broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

### Step 4.2: Install Python Supabase Client
```bash
pip3 install supabase python-dotenv
```

### Step 4.3: Update requirements.txt
```bash
cd /home/krishna/Projects/drip-irrigation/server
echo "supabase>=2.0.0" >> requirements.txt
```

---

## 🚀 Part 5: Run Complete System

### Terminal 1: Supabase (if not running)
```bash
cd /home/krishna/Projects/drip-irrigation/supabase/docker
docker-compose up -d
```

### Terminal 2: MQTT Broker (Mosquitto)
```bash
sudo systemctl start mosquitto
```

### Terminal 3: MQTT Test Server
```bash
cd /home/krishna/Projects/drip-irrigation/server
python3 mqtt_test_server.py
```

### Terminal 4: MQTT to Supabase Bridge
```bash
cd /home/krishna/Projects/drip-irrigation/server
python3 mqtt_supabase_bridge.py
```

### Terminal 5: Monitor ESP32
```bash
screen /dev/ttyUSB0 115200
```

---

## 📱 Part 6: Access Points

### Supabase Dashboard
- **URL**: http://192.168.1.100:3000
- **Purpose**: Manage database, view data, run SQL queries

### Supabase API
- **URL**: http://192.168.1.100:8000
- **Purpose**: REST API for mobile app

### Supabase Realtime
- **URL**: ws://192.168.1.100:8000/realtime/v1/websocket
- **Purpose**: Real-time subscriptions

---

## 🧪 Part 7: Test the System

### Test 1: Insert Device Data
```bash
# From ESP32, sensor data will automatically flow:
ESP32 → MQTT → Bridge → Supabase
```

### Test 2: Query Data via API
```bash
# Get all devices
curl http://192.168.1.100:8000/rest/v1/devices \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# Get latest sensor data
curl "http://192.168.1.100:8000/rest/v1/sensor_data?device_id=eq.smartkisan_test&order=timestamp.desc&limit=10" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

### Test 3: View Data in Dashboard
1. Go to http://192.168.1.100:3000
2. Click **Table Editor**
3. Select `sensor_data` table
4. See real-time data from ESP32!

---

## 📊 Part 8: Network Architecture Update

```
┌─────────────────────────────────────────────┐
│           Wi-Fi Router (imshiva2)           │
│              192.168.1.1                    │
└──────┬──────────────┬───────────────────────┘
       │              │
   ┌───▼────┐     ┌──▼─────────────┐
   │ ESP32  │     │ Laptop Server  │
   │        │     │ 192.168.1.100  │
   └───┬────┘     │                │
       │          │ ┌────────────┐ │
       │          │ │ Mosquitto  │ │
       │          │ │  :1883     │ │
       │          │ └──────┬─────┘ │
       │          │        │       │
       └──────MQTT────────►│       │
                  │        │       │
                  │   ┌────▼────┐  │
                  │   │ Bridge  │  │
                  │   └────┬────┘  │
                  │        │       │
                  │   ┌────▼────┐  │
                  │   │Supabase │  │
                  │   │:8000    │  │
                  │   │:3000    │  │
                  │   └────┬────┘  │
                  │        │       │
                  │   ┌────▼────┐  │
                  │   │Postgres │  │
                  │   │Database │  │
                  │   └─────────┘  │
                  └────────────────┘
```

---

## 🔒 Part 9: Security Configuration

### Enable Authentication
In Supabase Dashboard:
1. Go to **Authentication** → **Settings**
2. Enable email/password auth
3. Configure email templates
4. Set password requirements

### Create API Keys
```bash
# In Supabase dashboard, go to Settings → API
# Copy:
# - anon (public) key → Use in mobile app
# - service_role key → Use in server only (keep secret!)
```

### Secure Row Level Security (RLS)
Update policies to restrict access:
```sql
-- Only allow users to see their own devices
DROP POLICY "Enable all for authenticated users" ON devices;

CREATE POLICY "Users can view their own devices" ON devices
  FOR SELECT USING (auth.uid() = owner_id);

-- Add owner_id column
ALTER TABLE devices ADD COLUMN owner_id UUID REFERENCES auth.users(id);
```

---

## 📈 Part 10: Performance Tuning

### Database Indexing
```sql
-- Add indexes for common queries
CREATE INDEX idx_sensor_data_recent 
  ON sensor_data(device_id, timestamp DESC) 
  WHERE timestamp > NOW() - INTERVAL '7 days';

-- Materialized view for dashboard
CREATE MATERIALIZED VIEW device_summary AS
SELECT 
  d.device_id,
  d.device_name,
  d.last_seen,
  (SELECT timestamp FROM sensor_data 
   WHERE device_id = d.device_id 
   ORDER BY timestamp DESC LIMIT 1) as last_data_time,
  (SELECT COUNT(*) FROM irrigation_events 
   WHERE device_id = d.device_id 
   AND start_time > NOW() - INTERVAL '24 hours') as events_24h
FROM devices d;

-- Refresh periodically
REFRESH MATERIALIZED VIEW device_summary;
```

### Data Retention Policy
```sql
-- Delete old sensor data (keep 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
  DELETE FROM sensor_data 
  WHERE timestamp < NOW() - INTERVAL '30 days';
  
  DELETE FROM system_logs 
  WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Run daily
SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data()');
```

---

## 🐛 Troubleshooting

### Issue: Docker containers won't start
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check logs
cd /home/krishna/Projects/drip-irrigation/supabase/docker
docker-compose logs
```

### Issue: Can't access Supabase dashboard
```bash
# Check if port 3000 is in use
sudo netstat -tuln | grep 3000

# Check firewall
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

### Issue: Database connection errors
```bash
# Check PostgreSQL container
docker-compose ps

# Connect to database directly
docker exec -it supabase-db psql -U postgres

# Inside psql:
\l  # List databases
\dt  # List tables
\q  # Quit
```

### Issue: Bridge not storing data
```bash
# Check Supabase URL and key in bridge script
# Get ANON_KEY from:
cat /home/krishna/Projects/drip-irrigation/supabase/docker/.env | grep ANON_KEY

# Test API manually:
curl http://192.168.1.100:8000/rest/v1/devices \
  -H "apikey: YOUR_KEY_HERE" \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

---

## 📱 Part 11: Mobile App Integration (Future)

### React Native Example
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'http://192.168.1.100:8000',
  'YOUR_ANON_KEY'
)

// Get latest sensor data
const { data, error } = await supabase
  .from('sensor_data')
  .select('*')
  .eq('device_id', 'smartkisan_test')
  .order('timestamp', { ascending: false })
  .limit(10)

// Real-time subscription
const subscription = supabase
  .channel('sensor_updates')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'sensor_data' },
    (payload) => {
      console.log('New sensor data:', payload.new)
    }
  )
  .subscribe()
```

---

## ✅ Success Checklist

- [ ] Docker and Docker Compose installed
- [ ] Supabase running (docker-compose up)
- [ ] Dashboard accessible at http://192.168.1.100:3000
- [ ] Database tables created
- [ ] Test device inserted
- [ ] MQTT to Supabase bridge running
- [ ] ESP32 data flowing to database
- [ ] Can query data via API
- [ ] Can view data in dashboard

---

## 🎯 Quick Start Commands

```bash
# Start Supabase
cd /home/krishna/Projects/drip-irrigation/supabase/docker
docker-compose up -d

# Start MQTT bridge
cd /home/krishna/Projects/drip-irrigation/server
python3 mqtt_supabase_bridge.py

# View Supabase dashboard
firefox http://192.168.1.100:3000

# Stop Supabase
docker-compose down
```

---

**Estimated Setup Time**: 30-45 minutes
**Difficulty**: Medium
**Prerequisites**: Docker knowledge helpful but not required

Next: Create mobile app to visualize this data! 📱
