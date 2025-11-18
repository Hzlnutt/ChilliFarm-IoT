# 🔧 Troubleshooting Guide - IoT Chili Garden

**Panduan Lengkap untuk Mengatasi Masalah**

---

## 📋 Quick Troubleshooting Matrix

| Gejala | Penyebab | Solusi | Link |
|--------|----------|--------|------|
| MQTT Broker Error | Broker tidak berjalan | Lihat: Setup MQTT Broker | [Link](#setup-mqtt-broker) |
| Backend tidak connect | MQTT tidak aktif | Lihat: Backend Connection | [Link](#backend-mqtt-connection-error) |
| ESP32 WiFi Error | SSID/Password salah | Lihat: ESP32 WiFi | [Link](#esp32-wifi-connection-failed) |
| Data tidak muncul | Sensor/MQTT issue | Lihat: Data Flow | [Link](#no-data-in-api) |
| Pompa tidak respons | GPIO/Relay issue | Lihat: Actuator Control | [Link](#pump-not-responding) |
| Port 1883 sudah pakai | Another MQTT instance | Lihat: Port Conflict | [Link](#mqtt-port-already-in-use) |
| `curl` command error | Windows shell issue | Lihat: Windows curl | [Link](#curl-command-not-working) |

---

## 🔴 CRITICAL ERRORS

### ERROR 1: MQTT Broker tidak berjalan

#### 🔴 Gejala:
```
Error: connection refused
Error: [Errno 10061] No connection could be made
Backend log: [FAILED] Could not connect to MQTT
```

#### 🔍 Debugging Steps:

**Step 1**: Verifikasi Mosquitto terinstal
```bash
mosquitto --version
```
Output harusnya: `mosquitto version X.X.X`

Jika error `not found`:
```bash
# Install Mosquitto
# Download dari: https://mosquitto.org/download/
# Atau via Chocolatey:
choco install mosquitto
```

**Step 2**: Verifikasi port 1883 bebas
```bash
netstat -an | findstr 1883
```

Jika output kosong = port bebas ✅
Jika ada output = port sudah dipakai (lihat: Port Conflict)

**Step 3**: Start MQTT dengan explicit address
```bash
mosquitto -p 1883 -h 192.168.0.186
```

**Step 4**: Monitor MQTT status
```bash
tasklist | findstr mosquitto
```

Jika tidak muncul = MQTT tidak berjalan

#### ✅ Solusi:
```bash
# Terminal 1: Start MQTT Broker
mosquitto -p 1883

# Expected output:
# xxxx: Listening on port 1883.
```

✔️ MQTT sudah berjalan jika terminal menunjukkan "Listening on port 1883"

---

### ERROR 2: Backend MQTT Connection Error

#### 🔴 Gejala:
```
[FAILED] Could not connect to MQTT broker
[ERROR] MQTT connection failed: connection refused
Backend log tidak menunjukkan [OK] MQTT connected
```

#### 🔍 Debugging Steps:

**Step 1**: Pastikan MQTT broker berjalan
```bash
# Terminal 1 - check MQTT
netstat -an | findstr 1883
```

Harus menunjukkan: `TCP    192.168.0.186:1883    LISTENING`

**Step 2**: Verifikasi IP address di config
```bash
# Buka: backend/config.py
type backend\config.py | findstr MQTT_BROKER
```

Harus menunjukkan: `MQTT_BROKER='192.168.0.186'`

Jika berbeda, update dengan IP hotspot Anda:
```bash
# Cek IP dengan:
ipconfig
# Catat IPv4 Address
```

**Step 3**: Test MQTT connection secara langsung
```bash
# Terminal baru
cd backend
python -c "import paho.mqtt.client as mqtt; c=mqtt.Client(); c.connect('192.168.0.186',1883); print('OK')"
```

Jika output: `OK` = MQTT connection OK ✅
Jika timeout/error = IP atau broker bermasalah

**Step 4**: Check firewall
```bash
# Windows Defender Firewall - pastikan MQTT allowed
netsh advfirewall firewall show rule name=all | findstr 1883
```

#### ✅ Solusi:

1. Pastikan MQTT berjalan: `mosquitto -p 1883`
2. Verifikasi IP di `backend/config.py`
3. Restart backend: `python app.py`

Expected output:
```
[OK] MQTT connected to 192.168.0.186:1883
 * Running on http://192.168.0.186:5000
```

---

### ERROR 3: ESP32 WiFi Connection Failed

#### 🔴 Gejala:
ESP32 console menunjukkan:
```
Connecting to WiFi...
WiFi connection failed
WiFi status: (-1, b'STAT_NO_AP_FOUND')
```

#### 🔍 Debugging Steps:

**Step 1**: Verifikasi hotspot aktif
```bash
ipconfig | findstr -A 5 "Wireless"
```

Harus menunjukkan hotspot sudah enable dengan IP address.

**Step 2**: Check SSID & Password di code
```python
# Buka: esp32_garden_mqtt.py
# Lihat baris 28-29:
WIFI_SSID = "hotspotkeren"
WIFI_PASS = "87654321"
```

Samakan dengan hotspot Anda:
- **SSID**: Nama hotspot (case-sensitive!)
- **PASS**: Password hotspot

**Step 3**: Test dengan hardcoded credentials
```python
# Dalam esp32_garden_mqtt.py, update:
WIFI_SSID = "YOUR_HOTSPOT_SSID"    # Copy-paste exact name
WIFI_PASS = "YOUR_HOTSPOT_PASSWORD" # Exact password
```

**Step 4**: Restart ESP32 & check console
Lihat output di Thonny/VS Code console:
```
Connecting to WiFi...
WiFi status: (IP, ...)  ← Harus menunjukkan IP
Connected to MQTT broker
```

#### ✅ Solusi:

1. Turn ON hotspot
2. Update SSID & PASSWORD di `esp32_garden_mqtt.py`
3. Upload ulang ke ESP32
4. Check console untuk "WiFi status: (IP, ...)"

---

### ERROR 4: No Data in API

#### 🔴 Gejala:
```bash
curl http://192.168.0.186:5000/api/data/latest
```
Response: `null` atau empty `{}`

#### 🔍 Debugging Steps:

**Step 1**: Verifikasi backend berjalan
```bash
curl http://192.168.0.186:5000/api/health
```

Harus menunjukkan: `{"status": "ok", "mqtt": "connected"}`

Jika error = backend tidak berjalan, restart: `python app.py`

**Step 2**: Check MQTT topic yang benar
```bash
# Terminal baru - subscribe ke MQTT topic
mosquitto_sub -h 192.168.0.186 -p 1883 -t "esp32/chili/data"
```

Harus menerima data JSON dari ESP32 setiap 5 detik:
```json
{"temperature_c": 28.5, "humidity_pct": 65.0, ...}
```

Jika tidak ada data:
- ESP32 tidak terkoneksi MQTT
- MQTT topic salah
- Sensor tidak terbaca

**Step 3**: Test dengan data mock
```bash
mosquitto_pub -h 192.168.0.186 -p 1883 \
  -t "esp32/chili/data" \
  -m '{"temperature_c": 25.0, "humidity_pct": 60.0, "soil_moisture": 50, "ph": 6.8, "light_lux": 1000.0}'
```

Kemudian check API:
```bash
curl http://192.168.0.186:5000/api/data/latest
```

Harus return data yang baru dipublish:
```json
{"temperature_c": 25.0, "humidity_pct": 60.0, ...}
```

**Step 4**: Check ESP32 console
```
MQTT publish: esp32/chili/data
Payload: {...}
```

Jika tidak ada = ESP32 sensor tidak baca atau MQTT publish error.

#### ✅ Solusi:

1. Verifikasi backend: `curl http://192.168.0.186:5000/api/health`
2. Verifikasi MQTT topic: `mosquitto_sub -h 192.168.0.186 -t "esp32/chili/data"`
3. Test dengan mock data: `mosquitto_pub -h 192.168.0.186 -t "esp32/chili/data" -m '...'`
4. Check ESP32 console untuk sensor reading

---

### ERROR 5: Pump Not Responding

#### 🔴 Gejala:
```bash
curl -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
```
API returns 200 OK, tapi pompa tidak hidup.

#### 🔍 Debugging Steps:

**Step 1**: Verify API response
```bash
curl -v -X POST http://192.168.0.186:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
```

Harus menunjukkan:
```json
{"status": "ok", "pump": "on", "message": "Pump command sent"}
```

Jika error = API masalah, lihat backend logs.

**Step 2**: Check ESP32 console
```
MQTT message received: {"pump": "on"}
Pump ON (GPIO 26)
```

Jika tidak ada = MQTT command tidak terkirim atau subscribed topic salah.

**Step 3**: Test GPIO langsung
```python
# Di ESP32, manual test:
from machine import Pin
pump = Pin(26, Pin.OUT)
pump.on()   # Should activate relay
pump.off()  # Should deactivate relay
```

Jika pompa tidak respond = GPIO atau relay bermasalah.

**Step 4**: Check relay wiring
```
GPIO 26 ─────→ [Relay Coil +]
GND ──────────→ [Relay Coil -]
Relay NO ─────→ [Pump +]
Relay COM ────→ [12V/24V +]
Pump - ───────→ [12V/24V -]
```

Verifikasi dengan multimeter:
- Relay coil: continuity saat GPIO 26 HIGH
- Relay switch: continuity saat relay activated

#### ✅ Solusi:

1. Test API: `curl -X POST http://192.168.0.186:5000/api/control -H "Content-Type: application/json" -d '{"pump": "on"}'`
2. Check ESP32 console: harus terima MQTT message
3. Test GPIO manually: `pump = Pin(26, Pin.OUT); pump.on()`
4. Verify relay wiring dengan multimeter

---

## ⚠️ COMMON ERRORS

### MQTT Port Already in Use

#### 🔴 Gejala:
```
Error: Address already in use
Error: bind: Address already in use
Cannot start MQTT: [Errno 10048]
```

#### ✅ Solusi:

**Option 1**: Kill existing MQTT process
```bash
taskkill /IM mosquitto.exe /F
mosquitto -p 1883
```

**Option 2**: Use different port
```bash
mosquitto -p 1884
```
Kemudian update `backend/config.py`:
```python
MQTT_PORT = 1884  # Add this line
```

**Option 3**: Check what's using port 1883
```bash
netstat -ano | findstr 1883
# Copy PID number
taskkill /PID <PID> /F
```

---

### Windows curl Command Not Found

#### 🔴 Gejala:
```
'curl' is not recognized as an internal or external command
```

#### ✅ Solusi:

**Option 1**: Use PowerShell instead
```powershell
# Instead of:
curl http://192.168.0.186:5000/api/health

# Use:
Invoke-WebRequest -Uri "http://192.168.0.186:5000/api/health" | ConvertTo-Json
```

**Option 2**: Install curl
```bash
choco install curl
# Restart PowerShell, try again
```

**Option 3**: Use Python
```bash
python -c "import requests; print(requests.get('http://192.168.0.186:5000/api/health').json())"
```

---

### ESP32 Upload Timeout

#### 🔴 Gejala:
```
Timeout waiting for packet header
Error: espcomm_open failed
```

#### ✅ Solusi:

**Step 1**: Check USB connection
```bash
# Windows Device Manager:
# Cek apakah ESP32 muncul di COM ports
mode
```

**Step 2**: Verify MicroPython installed
```bash
# Using esptool.py:
esptool.py --chip esp32 -p COM3 read_mac
```

Harus return MAC address.

**Step 3**: Use Thonny IDE
1. Tools → Options → Interpreter
2. Pilih "MicroPython (ESP32)"
3. Select correct COM port
4. Click OK
5. Upload file: File → Open → esp32_garden_mqtt.py
6. Run: F5

---

### Database Lock Error

#### 🔴 Gejala:
```
sqlite3.OperationalError: database is locked
```

#### ✅ Solusi:

**Step 1**: Close all open connections
```bash
# Stop Flask backend
# Press Ctrl+C di terminal backend
```

**Step 2**: Delete lock file
```bash
cd backend
# Delete data.db-wal, data.db-shm jika ada
del data.db-wal
del data.db-shm
```

**Step 3**: Restart backend
```bash
python app.py
```

---

### CORS Error (Frontend Integration)

#### 🔴 Gejala:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

#### ℹ️ Info:

CORS sudah enabled di `backend/app.py`:
```python
CORS(app, 
     origins=["http://192.168.0.186:*", "http://localhost:*"],
     allow_headers=["Content-Type"],
     methods=["GET", "POST"])
```

#### ✅ Solusi:

**Option 1**: Frontend is at different origin
```python
# Edit: backend/app.py
# Add frontend origin:
CORS(app, 
     origins=["http://192.168.0.186:*", 
              "http://localhost:*",
              "http://YOUR_FRONTEND_IP:*"],
     allow_headers=["Content-Type"],
     methods=["GET", "POST"])
```

**Option 2**: Test with direct API call first
```bash
# Direct API call (no CORS issue)
curl http://192.168.0.186:5000/api/health
```

---

## 🟡 WARNINGS & BEST PRACTICES

### ⚠️ WiFi Disconnects Frequently

**Cause**: Hotspot signal weak atau WiFi profile issue

**Fix**:
```python
# Dalam esp32_garden_mqtt.py, add reconnect logic:
import time

for i in range(10):
    try:
        wlan.connect(WIFI_SSID, WIFI_PASS)
        # Wait for connection
        while not wlan.isconnected():
            time.sleep(1)
        break
    except:
        time.sleep(2)  # Retry after 2 seconds
```

---

### ⚠️ Sensor Reading Inconsistent

**Cause**: ADC noise, sensor connection loose

**Fix**:
```python
# Add averaging filter:
def read_soil_with_filter(samples=5):
    readings = []
    for _ in range(samples):
        readings.append(soil_adc.read())
        time.sleep(0.1)
    return sum(readings) // len(readings)

soil_val = read_soil_with_filter()
```

---

### ⚠️ High CPU Usage

**Cause**: Loop running too fast, no delay

**Fix**:
```python
# Ensure main loop has adequate delay:
while True:
    # ... read sensors ...
    time.sleep(5)  # 5 second minimum
```

---

## 🟢 VERIFICATION CHECKLIST

Sebelum consider "system working", pastikan:

- [ ] `mosquitto -p 1883` running tanpa error
- [ ] `curl http://192.168.0.186:5000/api/health` returns status "ok"
- [ ] `curl http://192.168.0.186:5000/api/data/latest` returns sensor data
- [ ] `mosquitto_sub -t "esp32/chili/data"` receives JSON every 5 seconds
- [ ] `/api/control` dengan pump "on" mengaktifkan relay
- [ ] Database file `backend/data.db` exists
- [ ] No errors di terminal backend dalam 1 menit
- [ ] No errors di ESP32 console dalam 1 menit

---

## 📞 ESCALATION PATH

Jika masalah tidak teratasi:

1. **Collect Logs** (1 menit)
   ```bash
   # Backend log
   python app.py 2>&1 | tee backend.log
   
   # MQTT log
   mosquitto -p 1883 -v 2>&1 | tee mqtt.log
   
   # Windows event viewer
   eventvwr.exe
   ```

2. **Run Validation** (2 menit)
   ```bash
   # Run all health checks
   curl http://192.168.0.186:5000/api/health
   curl http://192.168.0.186:5000/api/sensors
   curl http://192.168.0.186:5000/api/measurements
   ```

3. **Document Issue** (1 menit)
   ```
   - Error message (exact)
   - Steps to reproduce
   - Expected vs actual
   - Logs (copy-paste dari terminal)
   - System info (ipconfig, python version, etc.)
   ```

4. **Contact Support**
   - Sertakan dokumentasi dari step 3

---

## 📚 REFERENCE

- Backend logs: Terminal where `python app.py` runs
- MQTT logs: Terminal where `mosquitto -p 1883` runs
- ESP32 logs: Thonny IDE console atau serial monitor
- Database: `backend/data.db`
- Configuration: `backend/config.py`, `esp32_garden_mqtt.py`

---

**Last Updated**: November 18, 2025  
**Version**: Troubleshooting v1.0  
**Status**: ✅ Ready

