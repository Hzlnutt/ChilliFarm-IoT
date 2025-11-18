# ESP32 & Backend MQTT Synchronization Guide

## Overview
This document ensures **complete synchronization** between ESP32 MicroPython code and Flask backend to prevent errors during full system run.

---

## 1. MQTT Configuration Alignment

### ESP32 (MicroPython)
```python
# esp32_garden_mqtt.py
MQTT_BROKER = "192.168.0.186"      # ← Your laptop hotspot IP
MQTT_PORT = 1883

TOPIC_SENSORS = b"esp32/chili/data"    # ← Sends sensor data here
TOPIC_COMMANDS = b"esp32/chili/cmd"    # ← Receives commands here
```

### Flask Backend
```python
# backend/config.py
MQTT_BROKER = '192.168.0.186'          # ← Same as ESP32!
MQTT_PORT = 1883

MQTT_SENSOR_TOPIC = 'esp32/chili/data' # ← Listens to this
MQTT_COMMAND_TOPIC = 'esp32/chili/cmd' # ← Publishes here
```

### ✅ Verified Match
- Broker: `192.168.0.186` (local hotspot) ✓
- Port: `1883` ✓
- Sensor topic: `esp32/chili/data` ✓
- Command topic: `esp32/chili/cmd` ✓

---

## 2. Data Field Mapping

### ESP32 Publishes (on `esp32/chili/data`)
```json
{
  "device_id": "esp32_chili_01",
  "ts": "2025-11-18 10:30:45",
  "temperature_c": 28.5,
  "humidity_pct": 65.2,
  "soil_moisture": 55,
  "ph": 6.8,
  "light_lux": 1250.0
}
```

### Backend Parses & Stores

| ESP32 Field | Backend Sensor | Unit | Database |
|---|---|---|---|
| `temperature_c` | `DHT22_TEMP` | °C | Measurement.value |
| `humidity_pct` | `DHT22_HUMIDITY` | % | Measurement.value |
| `soil_moisture` | `SOIL_MOISTURE` | % | Measurement.value |
| `ph` | `PH_SENSOR` | pH | Measurement.value |
| `light_lux` | `BH1750` | lux | Measurement.value |

### ✅ Backend Handler Verification
From `app.py` line 31-51:
```python
def on_mqtt_message(topic, data):
    # ✓ temperature_c → DHT22_TEMP
    # ✓ humidity_pct → DHT22_HUMIDITY  
    # ✓ soil_moisture → SOIL_MOISTURE
    # ✓ ph → PH_SENSOR
    # ✓ light_lux → BH1750
```

---

## 3. Data Conversions

### Soil Moisture (ADC → Percentage)
**ESP32 converts to percentage:**
```python
# Raw ADC (0-4095) → Percentage (0-100%)
soil_percent = max(0, min(100, int((soil_val / 4095) * 100)))
data["soil_moisture"] = soil_percent  # Always 0-100 range
```

**Thresholds (for automation):**
```python
SOIL_DRY_THRESHOLD = 40    # < 40% = start watering
SOIL_WET_THRESHOLD = 70    # > 70% = stop watering
```

### pH Mapping
**ADC (0-4095) → pH (0-14):**
```python
PH_ADC_MIN = 0
PH_ADC_MAX = 4095
PH_MIN = 0.0
PH_MAX = 14.0

ph = 0 + (adc_value - 0) * (14.0 - 0) / (4095 - 0)
```

### Light Sensor (BH1750)
```python
# Direct lux reading, no conversion needed
data["light_lux"] = round(lux, 2)  # e.g., 1250.45 lux
```

---

## 4. MQTT Message Flow

```
┌─────────────────────────────────────────────────────────────┐
│ ESP32 (MicroPython)                                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Read sensors every 20 seconds (READ_INTERVAL)           │
│  2. Pack data as JSON                                        │
│  3. PUBLISH to "esp32/chili/data"                            │
│                                                               │
│     {                                                         │
│       "temperature_c": 28.5,                                │
│       "humidity_pct": 65.2,                                 │
│       "soil_moisture": 55,                                  │
│       "ph": 6.8,                                            │
│       "light_lux": 1250.0                                   │
│     }                                                         │
│                                                               │
│  4. SUBSCRIBE to "esp32/chili/cmd"                           │
│  5. Receive command (pump/servo control)                     │
│                                                               │
└────────────────────────┬────────────────────────────────────┘
                         │ MQTT Broker (192.168.0.186:1883)
                         │
┌────────────────────────▼────────────────────────────────────┐
│ Flask Backend                                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. MQTT Client connects to broker                           │
│  2. SUBSCRIBE to "esp32/chili/data"                          │
│  3. Receive message → Parse JSON                             │
│  4. Extract field (e.g., temperature_c)                      │
│  5. Find/Create sensor in database                           │
│  6. INSERT Measurement record                                │
│  7. REST API provides data to frontend                       │
│                                                               │
│     GET /api/data/latest                                     │
│     → Returns all latest sensor readings                     │
│                                                               │
│  8. PUBLISH commands to "esp32/chili/cmd" when needed        │
│     POST /api/control → {"pump": "on"}                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Pin Configuration

### ESP32 Hardware Pins
```python
# Sensors
PIN_DHT = 15           # Temperature & Humidity (3.3V)
PIN_PH_ADC = 35        # pH sensor (ADC input, 0-3.3V)
PIN_SOIL_ADC = 34      # Soil moisture (ADC input, 0-3.3V)

# I2C (Light sensor)
I2C_SDA = 21           # BH1750 data line
I2C_SCL = 22           # BH1750 clock line

# Actuators
PIN_PUMP = 26          # Pump relay (digital output)
PIN_SERVO = 27         # Valve servo (PWM output)
```

### Wiring Checklist
- [ ] DHT22 DATA → GPIO 15 (3.3V)
- [ ] pH sensor Po → GPIO 35 (5V sensor, output limited to 3.0V)
- [ ] Soil moisture → GPIO 34 (3.3V)
- [ ] BH1750 SDA → GPIO 21 (3.3V I2C)
- [ ] BH1750 SCL → GPIO 22 (3.3V I2C)
- [ ] Pump relay → GPIO 26 (5V relay, powered externally)
- [ ] Servo → GPIO 27 (PWM signal, external power)
- [ ] **ALL GND connected together** (ESP32, sensors, relay, servo)

---

## 6. Testing Checklist Before Full Run

### Prerequisites
```bash
# 1. MQTT Broker running on 192.168.0.186:1883
mosquitto -p 1883  # or check if already running

# 2. Backend running
cd backend
python app.py
# Should show: [OK] MQTT connected to 192.168.0.186:1883

# 3. Flask server listening
# Should show: Running on http://192.168.0.186:5000
```

### Step 1: Test Backend Alone
```bash
# In another terminal
curl http://192.168.0.186:5000/api/health
# Expected: {"status": "ok", "mqtt": "connected", ...}
```

### Step 2: Simulate ESP32 Data
```bash
# Publish test message from any MQTT client
mosquitto_pub -h 192.168.0.186 -p 1883 \
  -t "esp32/chili/data" \
  -m '{
    "device_id": "esp32_chili_01",
    "temperature_c": 28.5,
    "humidity_pct": 65.0,
    "soil_moisture": 55,
    "ph": 6.8,
    "light_lux": 1250.0
  }'

# Check if received by backend
curl http://192.168.0.186:5000/api/data/latest
# Should show the data just published
```

### Step 3: Deploy to ESP32
1. Connect ESP32 via USB
2. Upload `esp32_garden_mqtt.py` via MicroPython IDE
3. Verify console output:
   - `Connecting to WiFi...`
   - `WiFi status: ...`
   - `Connected to MQTT broker`
   - `Sensors: {...}`

### Step 4: Verify Data Flow
```bash
# Check if backend is receiving
curl http://192.168.0.186:5000/api/sensors
# Should show 5 sensors (DHT22_TEMP, DHT22_HUMIDITY, SOIL_MOISTURE, PH_SENSOR, BH1750)

curl http://192.168.0.186:5000/api/measurements
# Should show measurements from sensors
```

---

## 7. Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'routes.dashboard'"
**Fix:** Already removed from current config, but check `routes/__init__.py`:
```python
# ✓ Correct (API only)
from .api import api_bp

# ✗ Wrong (do not use)
from .dashboard import dashboard_bp
```

### Issue: "MQTT connection refused"
**Check:**
1. MQTT broker running: `netstat -an | grep 1883`
2. Correct IP: `192.168.0.186` (use `ipconfig` to verify)
3. Firewall allows port 1883
4. Backend config has same IP

### Issue: "Data not appearing in database"
**Debug:**
```python
# Check backend console for:
# [MQTT] esp32/chili/data: {'temperature_c': 28.5, ...}
# [OK] Measurement saved

# If not appearing:
# 1. Check /api/sensors endpoint
# 2. Verify JSON field names match exactly
# 3. Check database: sqlite3 data.db "SELECT * FROM measurement;"
```

### Issue: "Soil threshold never triggers watering"
**Verify thresholds:**
```python
# For percentage-based (0-100):
SOIL_DRY_THRESHOLD = 40    # Check if soil_moisture < 40
SOIL_WET_THRESHOLD = 70    # Check if soil_moisture > 70

# Test with test data:
mosquitto_pub -h 192.168.0.186 -p 1883 \
  -t "esp32/chili/data" \
  -m '{"soil_moisture": 35}'  # Should trigger dry alert
```

---

## 8. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND (Monorepo Partner)           │
│                    React/Vue/Next.js Dashboard                │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTP REST API
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                      FLASK BACKEND (5000)                     │
│                                                                │
│  Routes:                                                       │
│  ├─ GET /api/sensors (all sensor list)                        │
│  ├─ GET /api/measurements (all readings)                      │
│  ├─ GET /api/data/latest (latest from all sensors)            │
│  ├─ GET /api/data/average (avg/min/max over time)             │
│  ├─ POST /api/control (send pump/servo commands)              │
│  └─ GET /api/health (status check)                            │
│                                                                │
│  Database: SQLite (data.db)                                    │
│  ├─ Sensor (id, name, location)                               │
│  └─ Measurement (id, sensor_id, value, unit, timestamp)       │
│                                                                │
│  MQTT Client (paho-mqtt):                                     │
│  ├─ SUBSCRIBE: esp32/chili/data                               │
│  └─ PUBLISH: esp32/chili/cmd                                  │
│                                                                │
└────────────────────────────┬─────────────────────────────────┘
                             │ MQTT (1883)
                             │
┌────────────────────────────▼─────────────────────────────────┐
│              MQTT BROKER (192.168.0.186:1883)                │
│                  (Mosquitto / HiveMQ / etc)                   │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    ESP32 MICROCONTROLLER                      │
│                                                                │
│  Sensors:                   Actuators:                         │
│  ├─ DHT22 (Temp/Humidity)   ├─ Pump (relay)                   │
│  ├─ Soil Moisture (ADC)     └─ Servo (PWM)                    │
│  ├─ pH Sensor (ADC)                                            │
│  └─ BH1750 (Light/Lux)      MQTT:                             │
│                             ├─ PUBLISH: sensor data (20s)     │
│     Automation:             └─ SUBSCRIBE: commands            │
│     ├─ Read sensors (20s)                                      │
│     ├─ Send to MQTT                                            │
│     ├─ Receive commands                                        │
│     └─ Control actuators                                       │
│                                                                │
│     Irrigation Logic:                                          │
│     If soil < 40% → pump ON                                    │
│     If soil > 70% → pump OFF                                   │
│     Max pump runtime: 60 seconds                               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. What Changed (Summary of Fixes)

### ✅ Fixed in ESP32 Code
1. **MQTT Broker**: `broker.hivemq.com` → `192.168.0.186` (local)
2. **MQTT Topics**: Dynamic topics → Fixed topics matching backend
   - `sensors/{device_id}/data` → `esp32/chili/data`
   - `commands/{device_id}/set` → `esp32/chili/cmd`
3. **Soil Data**: Raw ADC values → Converted to percentage (0-100%)
4. **Soil Thresholds**: ADC values → Percentage values
5. **Logic**: Fixed dry/wet detection for percentage-based reading
6. **Field Names**: Removed `_raw` suffixes for cleaner API

### ✅ Verified in Backend
1. **Config**: MQTT broker, port, topics all match ESP32
2. **Data Handler**: All 5 sensor types properly parsed
3. **Database**: Sensors and Measurements correctly stored
4. **API**: All endpoints ready to serve data to frontend
5. **CORS**: Enabled for monorepo partner frontend access

---

## 10. Ready to Run Checklist

- [ ] MQTT broker running on `192.168.0.186:1883`
- [ ] Backend Flask app running (`python app.py`)
- [ ] ESP32 code uploaded with corrected MQTT config
- [ ] All sensors properly wired to GPIO pins
- [ ] pH sensor configured for 0-14 range
- [ ] Soil moisture ADC reading converts to 0-100%
- [ ] Pump/servo pins configured correctly
- [ ] WiFi SSID & password match your hotspot
- [ ] All GND connections verified
- [ ] Frontend ready to consume `/api` endpoints

---

## Need Help?

**Check Backend Logs:**
```bash
cd backend && python app.py
# Look for: [MQTT] esp32/chili/data: {...}
```

**Check ESP32 Console:**
```
Connected to MQTT broker
Sensors: {'temperature_c': 28.5, ...}
```

**Verify Database:**
```bash
sqlite3 backend/data.db
> SELECT * FROM sensor;
> SELECT * FROM measurement LIMIT 10;
```

**Test API:**
```bash
curl http://192.168.0.186:5000/api/health
curl http://192.168.0.186:5000/api/sensors
curl http://192.168.0.186:5000/api/data/latest
```

---

**Status: ✅ ESP32 & Backend Synchronized for Full System Run**

Generated: 2025-11-18  
Last Updated: Configuration fixed and verified
