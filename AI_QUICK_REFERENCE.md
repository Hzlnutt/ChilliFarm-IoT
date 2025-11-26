# Quick Reference - AI Control Endpoints

## Base URL
```
http://192.168.137.1:5000/api
```

---

## Endpoints Untuk AI

### 1. GET /ai/status
**Tujuan**: Ambil status lengkap sistem untuk AI decision making

**Request**:
```bash
curl http://192.168.137.1:5000/api/ai/status
```

**Response** (200):
```json
{
  "system": {
    "timestamp": "2025-11-26T14:30:45",
    "status": "operational",
    "mqtt": "connected"
  },
  "sensors": {
    "temperature": {"value": 28.5, "unit": "°C", "status": "normal"},
    "humidity": {"value": 65.2, "unit": "%", "status": "normal"},
    "soil_moisture": {"value": 35.0, "unit": "%", "status": "dry"},
    "light": {"value": 1200, "unit": "lux", "status": "normal"},
    "ph": {"value": 6.8, "unit": "pH", "status": "normal"}
  },
  "actuators": {
    "pump": {"state": "ON", "mode": "auto"},
    "servo": {"angle": 90, "state": "open"}
  },
  "recommendations": [...]
}
```

---

### 2. POST /ai/control
**Tujuan**: Kirim perintah kontrol pump/servo dari AI

**Request**:
```bash
curl -X POST http://192.168.137.1:5000/api/ai/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pump|servo",
    "command": "on|off|open|close|angle",
    "value": 90,
    "reason": "Explanation here",
    "auto_triggered": true
  }'
```

**Valid Commands**:
| Action | Command | Value Required | Example |
|--------|---------|-----------------|---------|
| pump | on | ❌ No | `{"action":"pump","command":"on"}` |
| pump | off | ❌ No | `{"action":"pump","command":"off"}` |
| servo | open | ❌ No | `{"action":"servo","command":"open"}` |
| servo | close | ❌ No | `{"action":"servo","command":"close"}` |
| servo | angle | ✅ Yes (0-180) | `{"action":"servo","command":"angle","value":45}` |

**Response** (200 Success):
```json
{
  "status": "success",
  "action": "pump",
  "command": "on",
  "result": "Pompa diatur ke ON",
  "previous_state": {"pump": "OFF", "servo_angle": 0},
  "new_state": {"pump": "ON", "reason": "..."},
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45"
}
```

**Response** (400 Error):
```json
{
  "status": "failed",
  "error": "Invalid pump command 'invalid'. Valid: on, off",
  "timestamp": "2025-11-26T14:30:45"
}
```

---

## Sensor Status Definitions

### Temperature Status
- `normal`: 20-30°C ✅
- `warning`: 15-20°C, 30-35°C ⚠️
- `critical`: <15°C, >35°C 🔴

### Humidity Status
- `normal`: 60-85% ✅
- `warning`: 40-60%, 85-95% ⚠️
- `critical`: <40%, >95% 🔴

### Soil Moisture Status
- `dry`: <30% 🏜️
- `warning_dry`: 30-40% ⚠️
- `normal`: 40-70% ✅
- `warning_wet`: 70-80% ⚠️
- `wet`: >80% 💧

### Light Status
- `normal`: 1000-10000 lux ✅
- `warning`: 500-1000 lux, >10000 lux ⚠️
- `critical`: <500 lux 🔴

### pH Status
- `normal`: 6.0-7.5 ✅
- `warning`: 5.5-6.0, 7.5-8.0 ⚠️
- `critical`: <5.5, >8.0 🔴

---

## Complete Examples

### Example 1: Pump ON (Dry Soil)
```bash
curl -X POST http://192.168.137.1:5000/api/ai/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pump",
    "command": "on",
    "reason": "Soil moisture 35%, below 40% threshold",
    "auto_triggered": true
  }'
```

### Example 2: Servo Open (Cooling)
```bash
curl -X POST http://192.168.137.1:5000/api/ai/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "servo",
    "command": "open",
    "reason": "Temperature 32°C, open lid for cooling",
    "auto_triggered": true
  }'
```

### Example 3: Servo Partial (Ventilation)
```bash
curl -X POST http://192.168.137.1:5000/api/ai/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "servo",
    "command": "angle",
    "value": 45,
    "reason": "Partial opening for ventilation",
    "auto_triggered": true
  }'
```

### Example 4: Pump OFF (Wet Soil)
```bash
curl -X POST http://192.168.137.1:5000/api/ai/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pump",
    "command": "off",
    "reason": "Soil moisture 78%, above 70% threshold",
    "auto_triggered": true
  }'
```

---

## Automation Decision Rules

### Pump Logic (Auto Mode)
```
IF soil_moisture < 40% AND pump_state == "OFF"
  → Turn pump ON (if min_off_time satisfied)
ELSE IF soil_moisture > 70% AND pump_state == "ON"
  → Turn pump OFF
ELSE IF pump_running_time > 60s
  → Turn pump OFF (safety limit)
```

### Servo Logic (Auto Mode)
```
IF temperature > 30°C
  → Open lid (90°) for cooling
ELSE IF temperature < 20°C
  → Close lid (0°) to retain heat
ELSE IF humidity > 85%
  → Open lid partially (60°) for ventilation
ELSE IF conditions optimal
  → Keep current state
```

---

## Frontend Integration

### Start AI Automation
```javascript
const controller = new GeminiAIController(GEMINI_API_KEY, API_BASE);
await controller.start(); // Polling setiap 10 detik
```

### Stop AI
```javascript
controller.stop();
```

### Get Statistics
```javascript
controller.getStats();
// Returns: {
//   total_decisions: 12,
//   successful: 11,
//   failed: 1,
//   success_rate: "91.67%",
//   pump_actions: 5,
//   servo_actions: 4
// }
```

### Change Poll Interval
```javascript
controller.setPollInterval(5000);  // 5 detik
controller.setPollInterval(10000); // 10 detik (default)
controller.setPollInterval(30000); // 30 detik
```

---

## Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 200 | Success | ✅ Command executed |
| 400 | Invalid action/command/value | ❌ Check request format |
| 500 | MQTT not initialized | ❌ Backend not connected to MQTT |
| 500 | Server error | ❌ Check backend logs |

---

## Response Time

| Endpoint | Expected | Notes |
|----------|----------|-------|
| GET /ai/status | < 200ms | Fast database query |
| POST /ai/control | < 500ms | Includes MQTT publish |
| MQTT execution | < 1s | Hardware reaction time |

---

## Tips & Tricks

### 1. Monitor Decisions
```javascript
// Check last decision in console
aiController.getLog()[aiController.getLog().length - 1]
```

### 2. View All Decisions
```javascript
aiController.getLog()
```

### 3. Real-time Status Check
```bash
# Monitor pump status
watch -n 1 'curl -s http://192.168.137.1:5000/api/ai/status | jq .actuators.pump'
```

### 4. Manual Override
```bash
# Turn pump ON manually (override AI)
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
```

---

## Network Requirements

- **Backend**: `http://192.168.137.1:5000`
- **MQTT**: `192.168.137.1:1883`
- **Gemini API**: `https://generativelanguage.googleapis.com`

Pastikan network connectivity:
```bash
ping 192.168.137.1
ping generativelanguage.googleapis.com
```

---

## Setup Checklist

- [ ] Gemini API Key diperoleh
- [ ] API Key dimasukkan di App.jsx
- [ ] Backend running di `http://192.168.137.1:5000`
- [ ] MQTT broker connected
- [ ] Frontend loaded
- [ ] AI start button berfungsi
- [ ] Decision log muncul di console
- [ ] Pump/servo commands executed

---

**Last Updated**: 2025-11-26  
**Status**: ✅ Production Ready
