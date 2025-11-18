# IoT Chili Garden Backend - REST API Server

Backend Flask API untuk IoT monitoring system. API-only (no web dashboard) untuk monorepo integration.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Server

```bash
python app.py
```

Server akan berjalan di:
- Local: `http://127.0.0.1:5000`
- Network: `http://192.168.0.186:5000`

### 3. Check Health

```bash
curl http://192.168.0.186:5000/api/health
```

---

## Architecture

```
ESP32 (Sensors)
    ↓ MQTT Publish
    ↓ esp32/chili/data
MQTT Broker (192.168.0.186:1883)
    ↓ Subscribe
Flask Backend
    ↓ Save to SQLite
REST API (Port 5000)
    ↓ JSON responses
Frontend (Monorepo)
    ↓ Display & Control
```

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Sensors
```
GET /api/sensors              # All sensors
GET /api/sensors/<id>         # Specific sensor
```

### Measurements
```
GET /api/measurements                    # All (with filters)
GET /api/measurements/<id>/latest        # Latest reading
GET /api/measurements/sensor/<id>        # Sensor history
```

### Data Summary
```
GET /api/data/latest                     # Latest from all
GET /api/data/average?hours=24          # Averages
```

### Control
```
POST /api/control              # Send command to ESP32
```

---

## MQTT Configuration

**Topics:**
- Sensor Data: `esp32/chili/data`
- Commands: `esp32/chili/cmd`

**Broker:** `192.168.0.186:1883`

---

## Project Structure

```
backend/
├── app.py                # Main app
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── mqtt_handler/         # MQTT client
├── database/             # Models & DB
├── routes/               # API endpoints
└── data.db              # SQLite (auto-created)
```

---

## Configuration

File: `config.py`

```python
MQTT_BROKER = '192.168.0.186'
MQTT_PORT = 1883
MQTT_SENSOR_TOPIC = 'esp32/chili/data'
MQTT_COMMAND_TOPIC = 'esp32/chili/cmd'
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
```

---

## Frontend Integration

Base URL untuk API calls:
```
http://192.168.0.186:5000/api
```

Contoh dengan JavaScript:
```javascript
// Get latest data
const data = await fetch('http://192.168.0.186:5000/api/data/latest')
  .then(r => r.json());

// Send command
await fetch('http://192.168.0.186:5000/api/control', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pump: 'on' })
});
```

---

## Database

SQLite database dengan 2 tables:

**sensors**
```
id | name | location
```

**measurements**
```
id | sensor_id | value | unit | timestamp
```

Query examples:
```bash
sqlite3 data.db "SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 10;"
sqlite3 data.db "SELECT AVG(value) FROM measurements WHERE sensor_id=1;"
```

---

## Testing

Check configuration:
```bash
python test_config.py
```

Test API:
```bash
python test_api.py
```

---

## Sensor Types

| Sensor | Unit | Range |
|--------|------|-------|
| DHT22_TEMP | °C | -40 to 125 |
| DHT22_HUMIDITY | % | 0 to 100 |
| SOIL_MOISTURE | % | 0 to 100 |
| PH_SENSOR | pH | 0 to 14 |
| BH1750 | lux | 1 to 65536 |

---

## Troubleshooting

**MQTT Connection Failed**
- Pastikan broker running di 192.168.0.186:1883
- Test: `mosquitto_sub -h 192.168.0.186 -t "#"`

**API Not Responding**
- Check server running: `python app.py`
- Check port: `netstat -an | findstr :5000`
- Test: `curl http://127.0.0.1:5000/api/health`

**No Sensor Data**
- Check ESP32 publishing to `esp32/chili/data`
- Verify database created: `ls -la data.db`

---

## Features

✅ REST API only (no web UI)
✅ CORS enabled
✅ MQTT real-time data ingestion
✅ SQLite persistent storage
✅ JSON responses
✅ Health check
✅ Device control
✅ Data averaging & history
✅ Multiple sensors

---

## Notes

- IPv4: `192.168.0.186`
- Port: `5000`
- CORS: Enabled untuk monorepo
- Database: Auto-created (`data.db`)
- Timestamps: UTC (ISO 8601)

Sistem monitoring dan kontrol tanaman cabai berbasis IoT dengan arsitektur:
```
ESP32 → MQTT Broker → Flask Backend → Web Frontend
```

## Arsitektur Sistem

```
┌─────────────┐
│   ESP32     │
│  Sensors &  │
│  Actuators  │
└──────┬──────┘
       │
    MQTT Pub/Sub
       │
┌──────▼──────────────────┐
│   MQTT Broker           │
│  (broker.hivemq.com)    │
└──────┬──────────────────┘
       │
┌──────▼──────────────────────┐
│   Flask Backend             │
│  - REST API                 │
│  - Database (SQLite)        │
│  - MQTT Subscribe/Publish   │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────┐
│   Web Frontend          │
│  - Dashboard            │
│  - Real-time Display    │
│  - Control Panel        │
└─────────────────────────┘
```

## Alur Data

### 1. **Sensor → Backend**
```
ESP32 (DHT22, Soil, pH, BH1750)
  ↓ MQTT Publish
Topic: sensors/esp32_chili_01/data
  ↓
Flask Backend (subscribe)
  ↓
SQLite Database
  ↓
REST API → Frontend Display
```

### 2. **Control → ESP32**
```
Frontend (Button Click)
  ↓ POST /api/control
Flask Backend
  ↓ MQTT Publish
Topic: commands/esp32_chili_01/set
  ↓
ESP32 (subscribe)
  ↓ Execute (Pump, Servo)
Status → MQTT Publish → Backend
```

## Setup & Installation

### Prerequisites
- Python 3.7+
- pip package manager
- MQTT Broker aktif (default: broker.hivemq.com)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Konfigurasi (opsional)
Edit `config.py` jika perlu mengubah:
- `MQTT_BROKER`: alamat broker MQTT
- `MQTT_PORT`: port MQTT (default: 1883)
- `MQTT_TOPIC`: topic sensor yang di-subscribe
- `DATABASE_URL`: path database SQLite

### 3. Jalankan Flask Server
```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

## REST API Endpoints

### 1. **GET /api/sensors**
Mendapatkan daftar semua sensor.

**Response:**
```json
[
  {
    "id": 1,
    "name": "DHT22",
    "location": "Living Room"
  }
]
```

### 2. **GET /api/status**
Mendapatkan pembacaan sensor terbaru.

**Response:**
```json
{
  "DHT22": {
    "location": "Living Room",
    "value": 28.5,
    "unit": "°C",
    "timestamp": "2025-11-18T10:30:45"
  },
  "Soil Moisture": {
    "location": "Chili Plant",
    "value": 350,
    "unit": "ADC",
    "timestamp": "2025-11-18T10:30:45"
  }
}
```

### 3. **POST /api/control**
Mengirim perintah kontrol ke ESP32 via MQTT.

**Request Body:**
```json
{
  "pump": "on|off|auto",
  "servo": 0-180,
  "auto": true|false
}
```

**Example - Nyalakan Pompa:**
```bash
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
```

**Example - Set Servo 45°:**
```bash
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"servo": 45}'
```

**Example - Enable Auto Mode:**
```bash
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"auto": true}'
```

**Response:**
```json
{
  "status": "ok",
  "message": "Command sent to esp32_chili_01",
  "command": {
    "pump": "on"
  }
}
```

### 4. **POST /api/measurements**
Menambah measurement manual (opsional).

**Request:**
```json
{
  "sensor_id": 1,
  "value": 28.5,
  "unit": "°C"
}
```

## Project Structure

```
backend/
├── app.py                    # Flask app factory
├── config.py               # Konfigurasi
├── requirements.txt        # Dependencies
│
├── mqtt_handler/
│   ├── __init__.py
│   └── mqtt_client.py      # MQTT client implementation
│
├── database/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models (Sensor, Measurement)
│   └── db_init.py          # Database initialization
│
├── routes/
│   ├── __init__.py
│   ├── api.py              # REST API endpoints
│   └── dashboard.py        # Web dashboard routes
│
├── templates/
│   ├── dashboard.html      # Main dashboard
│   └── sensor_table.html   # Sensor table view
│
└── static/
    ├── css/
    │   └── style.css       # Dashboard styling
    └── js/
        └── main.js         # Dashboard JavaScript
```

## Database Schema

### Sensor Table
```
- id: Integer (Primary Key)
- name: String (e.g., "DHT22", "Soil Moisture")
- location: String (e.g., "Living Room", "Chili Plant")
```

### Measurement Table
```
- id: Integer (Primary Key)
- sensor_id: Integer (Foreign Key → Sensor.id)
- value: Float (sensor reading)
- unit: String (e.g., "°C", "ADC", "pH")
- timestamp: DateTime (when measurement was taken)
```

## MQTT Topics

### Publish (ESP32 → Flask)
```
sensors/esp32_chili_01/data

Payload:
{
  "device_id": "esp32_chili_01",
  "ts": "2025-11-18 10:30:45",
  "temperature_c": 28.5,
  "humidity_pct": 65.0,
  "soil_raw": 350,
  "ph": 6.8,
  "lux": 1250.0
}
```

### Subscribe (Flask → ESP32)
```
commands/esp32_chili_01/set

Payload:
{
  "pump": "on|off|auto",
  "servo": 0-180,
  "auto": true|false
}
```

## Troubleshooting

### 1. **"MQTT connection failed"**
- Cek koneksi internet
- Pastikan broker MQTT aktif dan accessible
- Cek `MQTT_BROKER` dan `MQTT_PORT` di config.py

### 2. **"Database locked"**
- Hanya satu Flask instance yang boleh menulis ke database
- Gunakan fresh session untuk setiap request

### 3. **Sensor data tidak muncul**
- Pastikan ESP32 sudah terhubung WiFi
- Cek ESP32 publish ke topic yang benar: `sensors/esp32_chili_01/data`
- Monitor MQTT broker dengan: `mosquitto_sub -h broker.hivemq.com -t "sensors/#"`

### 4. **ESP32 tidak menerima perintah**
- Pastikan ESP32 subscribe ke topic: `commands/esp32_chili_01/set`
- Test publish dengan: `mosquitto_pub -h broker.hivemq.com -t "commands/esp32_chili_01/set" -m '{"pump":"on"}'`

## Testing Flow

### 1. Jalankan Backend
```bash
cd backend
python app.py
```

### 2. Buka Dashboard
```
http://localhost:5000
```

### 3. Test MQTT dengan MQTT Client
```bash
# Simulate ESP32 sensor data
mosquitto_pub -h broker.hivemq.com \
  -t "sensors/esp32_chili_01/data" \
  -m '{"temperature_c":28.5,"humidity_pct":65.0,"soil_raw":350,"ph":6.8,"lux":1250}'

# Simulate receiving command on ESP32
mosquitto_sub -h broker.hivemq.com \
  -t "commands/esp32_chili_01/set"
```

### 4. Test API dengan curl
```bash
# Get sensor status
curl http://localhost:5000/api/status

# Control pump
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump":"on"}'
```

## Notes

- Database akan otomatis di-create di path: `backend/data.db`
- MQTT client berjalan di background thread
- Dashboard auto-refresh sensor data setiap 5 detik
- Semua perintah kontrol di-publish async ke MQTT

## Future Enhancements

- [ ] User authentication
- [ ] Data logging & analytics
- [ ] Alert system (sensor threshold)
- [ ] Mobile app
- [ ] Cloud storage integration
- [ ] Multiple device support
