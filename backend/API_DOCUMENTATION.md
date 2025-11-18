# IoT Chili Garden - REST API Documentation

## Server Information

- **API URL**: `http://192.168.0.186:5000`
- **Base Path**: `/api`
- **Protocol**: HTTP (REST)
- **Format**: JSON
- **CORS**: Enabled (untuk monorepo frontend)

## Configuration

```
MQTT Broker: 192.168.0.186:1883
Sensor Topic: esp32/chili/data
Command Topic: esp32/chili/cmd
Database: SQLite (data.db)
```

## API Endpoints

### 1. Health & Info

#### GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-18T10:30:45.123456",
  "mqtt": "connected",
  "broker": "192.168.0.186",
  "port": 1883
}
```

#### GET `/api/info`
API information dan list semua endpoints

**Response:**
```json
{
  "name": "IoT Chili Garden Backend API",
  "version": "1.0.0",
  "api_version": "v1",
  "base_url": "/api",
  "mqtt_broker": "192.168.0.186",
  "mqtt_port": 1883,
  "endpoints": {
    "sensors": {...},
    "measurements": {...},
    "data": {...},
    "control": {...}
  }
}
```

---

### 2. Sensors

#### GET `/api/sensors`
Get all sensors dalam sistem

**Query Parameters:** Tidak ada

**Response:**
```json
[
  {
    "id": 1,
    "name": "DHT22_TEMP",
    "location": "Chili Plant"
  },
  {
    "id": 2,
    "name": "DHT22_HUMIDITY",
    "location": "Chili Plant"
  },
  {
    "id": 3,
    "name": "SOIL_MOISTURE",
    "location": "Chili Plant"
  },
  {
    "id": 4,
    "name": "PH_SENSOR",
    "location": "Chili Plant"
  },
  {
    "id": 5,
    "name": "BH1750",
    "location": "Chili Plant"
  }
]
```

#### GET `/api/sensors/<id>`
Get specific sensor by ID

**Path Parameters:**
- `id` (integer): Sensor ID

**Response:**
```json
{
  "id": 1,
  "name": "DHT22_TEMP",
  "location": "Chili Plant"
}
```

---

### 3. Measurements

#### GET `/api/measurements`
Get all measurements dengan filtering

**Query Parameters:**
- `sensor_id` (integer, optional): Filter by sensor ID
- `limit` (integer, default: 100): Max results
- `hours` (integer, default: 24): Data dari N jam terakhir

**Example:**
```
GET /api/measurements?sensor_id=1&limit=50&hours=12
```

**Response:**
```json
[
  {
    "id": 1,
    "sensor_id": 1,
    "sensor_name": "DHT22_TEMP",
    "value": 28.5,
    "unit": "C",
    "timestamp": "2025-11-18T10:30:45"
  }
]
```

#### GET `/api/measurements/<sensor_id>/latest`
Get latest reading untuk specific sensor

**Response:**
```json
{
  "id": 100,
  "sensor_id": 1,
  "sensor_name": "DHT22_TEMP",
  "value": 28.5,
  "unit": "C",
  "timestamp": "2025-11-18T10:30:45"
}
```

#### GET `/api/measurements/sensor/<sensor_id>`
Get semua measurements untuk specific sensor dengan paging

**Query Parameters:**
- `limit` (integer, default: 100): Max results
- `hours` (integer, default: 24): Data dari N jam terakhir
- `order` (string, default: 'desc'): 'asc' atau 'desc'

**Response:**
```json
{
  "sensor_id": 1,
  "sensor_name": "DHT22_TEMP",
  "sensor_location": "Chili Plant",
  "count": 45,
  "measurements": [
    {
      "id": 100,
      "value": 25.0,
      "unit": "C",
      "timestamp": "2025-11-18T10:10:00"
    }
  ]
}
```

---

### 4. Data Summary

#### GET `/api/data/latest`
Get latest reading dari semua sensors

**Response:**
```json
{
  "timestamp": "2025-11-18T10:30:45.123456",
  "sensors": {
    "DHT22_TEMP": {
      "sensor_id": 1,
      "location": "Chili Plant",
      "value": 28.5,
      "unit": "C",
      "timestamp": "2025-11-18T10:30:45"
    },
    "DHT22_HUMIDITY": {
      "sensor_id": 2,
      "location": "Chili Plant",
      "value": 65.0,
      "unit": "%",
      "timestamp": "2025-11-18T10:30:45"
    },
    "SOIL_MOISTURE": {
      "sensor_id": 3,
      "location": "Chili Plant",
      "value": 45.5,
      "unit": "%",
      "timestamp": "2025-11-18T10:30:45"
    },
    "PH_SENSOR": {
      "sensor_id": 4,
      "location": "Chili Plant",
      "value": 6.8,
      "unit": "pH",
      "timestamp": "2025-11-18T10:30:45"
    },
    "BH1750": {
      "sensor_id": 5,
      "location": "Chili Plant",
      "value": 1250,
      "unit": "lux",
      "timestamp": "2025-11-18T10:30:45"
    }
  }
}
```

#### GET `/api/data/average`
Get average values untuk semua sensors

**Query Parameters:**
- `hours` (integer, default: 24): Calculate average untuk N jam terakhir
- `sensor_id` (integer, optional): Specific sensor only

**Response:**
```json
{
  "period_hours": 24,
  "sensors": {
    "DHT22_TEMP": {
      "location": "Chili Plant",
      "average": 27.3,
      "min": 25.0,
      "max": 30.5,
      "count": 48,
      "unit": "C"
    }
  }
}
```

---

### 5. Control

#### POST `/api/control`
Send command ke ESP32 via MQTT

**Request Body:**
```json
{
  "pump": "on|off|auto",
  "servo": 0-180,
  "auto": true|false
}
```

**Examples:**

```bash
# Pump ON
curl -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'

# Set Servo 45 degrees
curl -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"servo": 45}'

# Enable Auto Mode
curl -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"auto": true}'
```

**Response:**
```json
{
  "status": "ok",
  "message": "Command sent to device",
  "command": {
    "pump": "on"
  }
}
```

---

## MQTT Topics

### Subscribe (ESP32 → Backend)
```
Topic: esp32/chili/data
Payload:
{
  "temperature_c": 28.5,
  "humidity_pct": 65.0,
  "soil_moisture": 45.5,
  "ph": 6.8,
  "light_lux": 1250.0
}
```

### Publish (Backend → ESP32)
```
Topic: esp32/chili/cmd
Payload:
{
  "pump": "on|off|auto",
  "servo": 0-180,
  "auto": true|false
}
```

---

## Usage Examples

### JavaScript/Fetch

```javascript
// Get latest data
fetch('http://192.168.0.186:5000/api/data/latest')
  .then(r => r.json())
  .then(data => console.log(data));

// Send control command
fetch('http://192.168.0.186:5000/api/control', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pump: 'on' })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

### Python/Requests

```python
import requests

# Get latest data
response = requests.get('http://192.168.0.186:5000/api/data/latest')
data = response.json()

# Send command
response = requests.post('http://192.168.0.186:5000/api/control',
  json={'pump': 'on'})
print(response.json())
```

### cURL

```bash
# Health check
curl http://192.168.0.186:5000/api/health

# Get all sensors
curl http://192.168.0.186:5000/api/sensors

# Get latest readings
curl http://192.168.0.186:5000/api/data/latest

# Get temperature history
curl "http://192.168.0.186:5000/api/measurements/sensor/1?hours=12&limit=20"

# Send pump on
curl -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump":"on"}'
```

---

## Notes

- IPv4: `192.168.0.186`
- MQTT Broker: `192.168.0.186:1883`
- Port: `5000`
- CORS enabled untuk monorepo frontend
- Timestamps dalam UTC (ISO 8601)
