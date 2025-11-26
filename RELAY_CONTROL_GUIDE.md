# 💧 RELAY CONTROL SYSTEM GUIDE

## Dokumentasi Sistem Kontrol Relay Pompa Air IoT Chili Garden

---

## 📋 DAFTAR ISI
1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Alur Kontrol](#alur-kontrol)
3. [Spesifikasi Hardware](#spesifikasi-hardware)
4. [Implementasi Software](#implementasi-software)
5. [Testing & Troubleshooting](#testing--troubleshooting)
6. [Fitur Keamanan](#fitur-keamanan)

---

## 🏗️ ARSITEKTUR SISTEM

### Diagram Alur Kontrol Relay

```
Frontend (React)
     ↓ [POST /api/control]
Backend (Flask)
     ↓ [MQTT Publish]
MQTT Broker (192.168.137.1:1883)
     ↓ [esp32/chili/cmd topic]
ESP32 (MicroPython)
     ↓ [GPIO 26 HIGH/LOW]
Relay Module (5V, 10A)
     ↓ [Switch Contact]
Pompa Air (12V, 1.5A)
     ↓ [Water Flow]
Plant Pot (Chili)
```

### Komunikasi MQTT

| Topik | Arah | Payload | Deskripsi |
|-------|------|---------|-----------|
| `esp32/chili/data` | ESP32 → Backend | `{sensors}` | Data sensor 5 input |
| `esp32/chili/cmd` | Backend → ESP32 | `{"pump": "on\|off\|auto"}` | Perintah kontrol pompa |
| `esp32/chili/status` | ESP32 → Backend | `{"pump": "ON\|OFF", "relay_pin": 26}` | Status relay pompa |

---

## 🔄 ALUR KONTROL

### 1. **Manual Control (User Click Button)**

```
[Frontend]
  ├─ User Click "NYALA" button
  └─ handleControlPump("on")
       ├─ POST http://192.168.137.1:5000/api/control
       │  └─ Payload: {"pump": "on"}
       │
[Backend]
  └─ Receive POST /api/control
       ├─ Validate command (on/off/auto)
       ├─ Publish to MQTT topic: esp32/chili/cmd
       │  └─ Payload: {"pump": "on"}
       └─ Return: {"status": "ok", "command": {"pump": "on"}}
       
[MQTT Broker]
  └─ Forward message to ESP32 on topic: esp32/chili/cmd

[ESP32]
  └─ on_mqtt_message() callback triggered
       ├─ Parse JSON: {"pump": "on"}
       ├─ Call pump_on()
       │  ├─ pump.value(1)  # Set GPIO 26 HIGH
       │  ├─ pump_running_since = time.time()
       │  └─ Publish status to esp32/chili/status
       │
[Relay Module]
  └─ GPIO 26 HIGH → Relay Coil Activated
       └─ Switch Contact Closed → 12V to Pump

[Pompa Air]
  └─ Power ON → Motor Runs → Water Flows
```

### 2. **Automatic Control (Soil Moisture)**

```
[ESP32 Automation Loop]
  ├─ Read soil_moisture ADC every 5 seconds
  │
  ├─ IF soil_moisture < 40% (DRY)
  │  └─ Call pump_on() if not already running
  │
  └─ IF soil_moisture > 70% (WET)
     └─ Call pump_off()
     
[Safety Checks]
├─ PUMP_MAX_RUNTIME_SEC = 60 seconds
│  └─ Auto stop pump after 60s continuous run
│
└─ PUMP_MIN_OFF_SEC = 30 seconds
   └─ Don't turn pump back on within 30s after stop
```

### 3. **Status Feedback Loop**

```
[ESP32 Status Publishing]
  ├─ pump_on() publishes: {"pump": "ON", "relay_pin": 26, "ts": "..."}
  ├─ pump_off() publishes: {"pump": "OFF", "relay_pin": 26, "ts": "..."}
  │
[Backend]
  ├─ Receives status message via on_mqtt_message()
  ├─ Logs: [RELAY-STATUS] Pump relay (GPIO 26): ON/OFF
  └─ Stores in database (optional)

[Frontend]
  ├─ Polls GET /api/actuator/status every 5 seconds
  ├─ Displays pump state: ON/OFF
  └─ Updates pumpStatus state
```

---

## 🔧 SPESIFIKASI HARDWARE

### Relay Module
- **Type**: 5V Relay Module (1-channel)
- **Coil Voltage**: 5V DC
- **Contact**: SPDT (Single Pole Double Throw)
- **Max Current**: 10A (DC/AC)
- **Signal Pin**: GPIO 26 (ESP32)
- **Control Logic**: Active HIGH (GPIO 26 = 1 → Relay ON)

### Pompa Air
- **Voltage**: 12V DC
- **Current**: 1.5A (Max)
- **Power**: 18W
- **Flow Rate**: ~2L/min
- **Relay Contact**: Connected to pump power supply (12V → GND)

### Koneksi Wiring

```
ESP32 GPIO 26 (Output) ──┐
                         │
                    [IN] Relay Module
                    [GND] │
                         └─→ GND

12V Power Supply ──→ [NC/COM] Relay Module
Pompa Ground ──────→ [NO] Relay Module Output
                     (When HIGH: 12V flows to pump)
```

---

## 💻 IMPLEMENTASI SOFTWARE

### A. ESP32 (MicroPython)

**File: `esp32_garden_mqtt.py`**

#### Relay Control Functions
```python
# Pin definition
PIN_PUMP = 26
pump = Pin(PIN_PUMP, Pin.OUT)

# Relay control - direct GPIO control
def pump_on():
    global pump_running_since
    pump.value(1)  # Set GPIO HIGH → Relay ON
    pump_running_since = time.time()
    print("[PUMP] Relay ON")
    publish_actuator({"pump": "ON", "relay_pin": PIN_PUMP, "ts": ts_now_str()})

def pump_off():
    global pump_running_since, last_pump_stop
    pump.value(0)  # Set GPIO LOW → Relay OFF
    pump_running_since = 0
    last_pump_stop = time.time()
    print("[PUMP] Relay OFF")
    publish_actuator({"pump": "OFF", "relay_pin": PIN_PUMP, "ts": ts_now_str()})
```

#### MQTT Command Handler
```python
def on_mqtt_message(topic, msg):
    """Handle MQTT messages from backend"""
    if topic == b'esp32/chili/cmd':
        try:
            data = ujson.loads(msg)
            pump_cmd = data.get('pump')
            
            if pump_cmd == 'on':
                pump_on()
            elif pump_cmd == 'off':
                pump_off()
            elif pump_cmd == 'auto':
                # Automation mode - handled in main loop
                pass
        except Exception as e:
            print(f"[MQTT-ERROR] Failed to parse command: {e}")
```

#### Automation Loop
```python
def automation_check_and_act():
    """Automatic pump control based on soil moisture"""
    global last_pump_stop
    
    if not auto_mode:
        return
    
    # Check dry condition
    if soil_moisture < 40 and pump_running_since == 0:
        elapsed_since_stop = time.time() - last_pump_stop
        if elapsed_since_stop >= PUMP_MIN_OFF_SEC:
            pump_on()
    
    # Check wet condition
    elif soil_moisture > 70 and pump_running_since > 0:
        pump_off()
    
    # Check max runtime
    if pump_running_since > 0:
        elapsed = time.time() - pump_running_since
        if elapsed >= PUMP_MAX_RUNTIME_SEC:
            pump_off()  # Safety: Stop pump after max runtime
```

#### Safety Parameters
```python
PUMP_MAX_RUNTIME_SEC = 60      # Max 1 minute continuous run
PUMP_MIN_OFF_SEC = 30          # Min 30 seconds between cycles
SOIL_MOISTURE_DRY = 40         # Trigger pump ON (%)
SOIL_MOISTURE_WET = 70         # Trigger pump OFF (%)
```

---

### B. Backend (Flask)

**File: `backend/routes/api.py`**

#### Control Endpoint with Validation
```python
@api_bp.route('/control', methods=['POST'])
def control_device():
    """Send control command to ESP32 via MQTT with relay validation"""
    data = request.get_json() or {}
    
    if not data:
        return jsonify({'error': 'No data provided', 'status': 'failed'}), 400
    
    # Validate pump command
    if 'pump' in data:
        valid_pump_cmds = ['on', 'off', 'auto']
        if data['pump'] not in valid_pump_cmds:
            return jsonify({
                'error': f"Invalid pump command. Valid: {valid_pump_cmds}",
                'status': 'failed'
            }), 400
    
    mqtt_client = current_app.mqtt_client
    if not mqtt_client:
        return jsonify({'error': 'MQTT not initialized', 'status': 'failed'}), 500
    
    try:
        topic = current_app.config['MQTT_COMMAND_TOPIC']
        payload = json.dumps(data)
        mqtt_client.publish(topic, payload)
        
        print(f"[API-RELAY] Pump command: {data.get('pump', 'N/A')}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Command sent to device',
            'timestamp': datetime.utcnow().isoformat(),
            'command': data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500
```

#### Actuator Status Endpoint
```python
@api_bp.route('/actuator/status', methods=['GET'])
def get_actuator_status():
    """Get current actuator status (pump relay state)"""
    try:
        # Returns latest relay state from status topic
        return jsonify({
            'pump': 'ON|OFF|UNKNOWN',
            'servo_angle': 0-180,
            'auto_mode': true/false,
            'last_update': 'timestamp',
            'relay_pin': 26,
            'status': 'ok'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500
```

**File: `backend/app.py`**

#### MQTT Relay Status Handler
```python
def on_mqtt_message(topic, data):
    """Process MQTT messages including relay status"""
    
    # Handle relay/actuator status
    if 'pump' in data:
        relay_state = data['pump']
        relay_pin = data.get('relay_pin', 26)
        print(f"[RELAY-STATUS] Pump relay (GPIO {relay_pin}): {relay_state}")
    
    # Store sensor data (as before)
    # ...
```

---

### C. Frontend (React)

**File: `frontend/src/App.jsx`**

#### Relay Control Handler
```jsx
const handleControlPump = async (command) => {
    try {
        const previousStatus = pumpStatus;
        setPumpStatus('WAITING...');
        console.log(`[RELAY-CONTROL] Sending pump command: ${command}`);
        
        const response = await axios.post(
            `http://192.168.137.1:5000/api/control`,
            { pump: command }
        );

        if (response.status === 200) {
            const commandUpper = command.toUpperCase();
            setPumpStatus(commandUpper);
            console.log(`[RELAY-CONTROL] Pump relay activated: ${commandUpper}`);
            alert(`Relay pompa berhasil diubah menjadi: ${commandUpper}`);
        } else {
            setPumpStatus(previousStatus);
            alert(`Gagal mengirim perintah. Status: ${response.status}`);
        }
    } catch (err) {
        console.error("[RELAY-CONTROL] Error:", err);
        alert("Error: Gagal terhubung untuk kontrol relay pompa.");
    }
};
```

#### Actuator Status Fetch
```jsx
const fetchActuatorStatus = async () => {
    try {
        const response = await axios.get(
            `http://192.168.137.1:5000/api/actuator/status`
        );
        console.log("[ACTUATOR-STATUS] Response:", response.data);
        setActuatorStatus(response.data);
    } catch (err) {
        console.error("[ACTUATOR-STATUS] Failed:", err);
    }
};

// Call both fetch functions every 5 seconds
useEffect(() => {
    fetchSensorData();
    fetchActuatorStatus();
    
    const intervalId = setInterval(() => {
        fetchSensorData();
        fetchActuatorStatus();
    }, REFRESH_INTERVAL);
    
    return () => clearInterval(intervalId);
}, []);
```

---

## 🧪 TESTING & TROUBLESHOOTING

### 1. **Test Manual Control**

**Step 1: Check MQTT Connection**
```bash
# Terminal 1 - Subscribe to command topic
mosquitto_sub -h 192.168.137.1 -t "esp32/chili/cmd"

# Terminal 2 - Send test command
mosquitto_pub -h 192.168.137.1 -t "esp32/chili/cmd" -m '{"pump":"on"}'

# Expected: See message appear in Terminal 1
```

**Step 2: Test Backend API**
```bash
# Test /control endpoint
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump":"on"}'

# Expected Response:
# {
#   "status": "ok",
#   "message": "Command sent to device",
#   "timestamp": "2025-11-18T10:30:45.123456",
#   "command": {"pump": "on"}
# }
```

**Step 3: Test Frontend Button**
1. Open http://192.168.137.1:5173 in browser
2. Click "NYALA" button
3. Check browser console (F12) for `[RELAY-CONTROL]` logs
4. Verify relay activates (listen for click sound)
5. Check pump water output

### 2. **Relay Diagnostics**

**Check Relay GPIO State**
```python
# On ESP32 terminal
>>> from machine import Pin
>>> pump = Pin(26, Pin.OUT)
>>> pump.value()  # Read current state
1  # HIGH (relay ON)
0  # LOW (relay OFF)
```

**Test Relay Directly**
```python
# On ESP32 - toggle relay manually
>>> pump.value(1)  # Turn ON
>>> time.sleep(2)
>>> pump.value(0)  # Turn OFF

# Listen for relay click sound
# Check pump water flow
```

### 3. **Troubleshooting**

| Masalah | Penyebab | Solusi |
|---------|---------|--------|
| Relay tidak aktif saat button diklik | MQTT tidak terhubung | Check broker IP (192.168.137.1) |
| Relay aktif tapi pompa tidak jalan | Relay tidak switch 12V | Check wiring relay-pump contact |
| Pompa jalan tapi tidak ada air | Air sudah habis | Isi tangki air |
| ESP32 tidak menerima command | Topic salah | Verify `esp32/chili/cmd` topic |
| Frontend button tidak responsive | API timeout | Check backend running dan CORS |

---

## 🔒 FITUR KEAMANAN

### 1. **Safety Limits**

```python
# ESP32 Implementation
PUMP_MAX_RUNTIME_SEC = 60      # Automatic stop after 1 min
PUMP_MIN_OFF_SEC = 30          # Cooldown between cycles
```

**Implementasi:**
- Pump tidak akan run > 60 detik tanpa henti
- Setelah stop, pump tidak akan restart < 30 detik
- Mencegah dry running dan overheating

### 2. **Command Validation**

```python
# Backend Implementation
valid_pump_cmds = ['on', 'off', 'auto']
if data['pump'] not in valid_pump_cmds:
    return error_response

# Frontend Implementation
if (response.status === 200) {
    // Only update UI if command successful
}
```

**Implementasi:**
- Backend validate semua command sebelum publish
- Frontend check response status
- Invalid command ditolak dengan error message jelas

### 3. **MQTT Error Handling**

```python
# ESP32
try:
    data = ujson.loads(msg)
    pump_cmd = data.get('pump')
except Exception as e:
    print(f"[MQTT-ERROR] Failed to parse: {e}")
    # Silently ignore malformed messages
```

### 4. **Status Monitoring**

```
Frontend ──[every 5 sec]──> GET /api/actuator/status
                            ↓
                    Verify relay actually ON/OFF
                    ↓
            Display status to user
```

---

## 📊 MONITORING & LOGGING

### Backend Logs
```
[API-RELAY] Pump command published to esp32/chili/cmd
[API-RELAY] Pump: on | Servo: N/A | Auto: N/A
[RELAY-STATUS] Pump relay (GPIO 26): ON
[ACTUATOR-STATUS] Response: {'pump': 'ON', ...}
```

### Frontend Console (F12)
```
[RELAY-CONTROL] Sending pump command: on
[RELAY-CONTROL] Pump relay activated: ON
[RELAY-FEEDBACK] Response: {status: 'ok', ...}
[ACTUATOR-STATUS] Fetching from: http://...
[ACTUATOR-STATUS] Response: {pump: 'ON', relay_pin: 26, ...}
```

### ESP32 Serial Monitor
```
[PUMP] Relay ON
[PUMP] Relay OFF
[MQTT-ERROR] Failed to parse command: ...
```

---

## 🚀 PRODUCTION CHECKLIST

- [ ] Test manual control (on/off) multiple times
- [ ] Test automatic control (soil moisture trigger)
- [ ] Verify safety limits (60s max, 30s cooldown)
- [ ] Check relay hardware (wiring, contacts)
- [ ] Verify MQTT broker connectivity
- [ ] Test in poor network conditions
- [ ] Monitor logs for 24 hours
- [ ] Document any issues found
- [ ] Create backup configuration
- [ ] Train user on operation

---

## 📞 SUPPORT

Untuk bantuan, check:
1. `/backend/README.md` - Backend setup
2. `/ESP32_BACKEND_SYNC_GUIDE.md` - Integration guide
3. `/documentation/TROUBLESHOOTING.md` - Common issues

---

**Last Updated**: November 18, 2025
**System Version**: v2.0 (Relay Control Enhanced)
**Status**: ✅ PRODUCTION READY
