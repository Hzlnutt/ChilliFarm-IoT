# Gemini AI Integration Guide - IoT Chili Garden

## Overview

Sistem IoT Chili Garden sekarang dilengkapi dengan **Gemini AI** untuk automasi cerdas. AI akan:
- Membaca status sensor secara real-time (temperature, humidity, soil moisture, light, pH)
- Membuat keputusan otomatis untuk kontrol pompa dan servo berdasarkan kondisi
- Menjalankan perintah kontrol via REST API
- Mencatat semua keputusan untuk audit trail

**Base URL**: `http://192.168.137.1:5000/api`

---

## Setup

### 1. Dapatkan Gemini API Key

1. Kunjungi [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Login dengan Google Account
3. Klik "Create API Key"
4. Copy API Key

### 2. Masukkan API Key di Frontend

Edit file `frontend/src/App.jsx`:

```javascript
const GEMINI_API_KEY = "YOUR_API_KEY_HERE";
```

Ganti `YOUR_API_KEY_HERE` dengan API Key yang sudah didapat.

### 3. Verifikasi Setup

Pastikan endpoint berikut bisa diakses:
- `GET http://192.168.137.1:5000/api/ai/status` - Check system status
- `POST http://192.168.137.1:5000/api/ai/control` - Send control commands

---

## How It Works

### Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│  Gemini AI Automation Loop (10 detik sekali)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GET /ai/status       │
         │  (fetch sensor data)  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌────────────────────────────┐
         │  Gemini API (gemini-pro)   │
         │  Decision Making            │
         │  (analyze & choose action)  │
         └───────────┬────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  POST /ai/control        │
         │  (execute pump/servo)    │
         └──────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  MQTT → ESP32            │
         │  (hardware control)      │
         └──────────────────────────┘
```

### Decision Logic

Gemini AI menggunakan logika berikut:

#### Pump Control
- **Turn ON** jika:
  - Soil moisture < 40% (tanah kering)
  - Pump tidak sedang running
  - Min off time sudah terpenuhi

- **Turn OFF** jika:
  - Soil moisture > 70% (tanah basah)
  - Pump sudah running > 60 detik

#### Servo Control (Lid)
- **Open (90°)** jika:
  - Temperature > 30°C (perlu pendinginan)
  - Humidity > 85% (kelembaban tinggi)

- **Close (0°)** jika:
  - Temperature < 20°C (perlu suhu hangat)

- **Partial angle** jika:
  - Perlu ventilasi tanpa perubahan ekstrem

---

## Frontend Integration

### Starting AI Automation

Di dashboard, klik tombol **"▶️ Start AI"** untuk memulai automasi.

```javascript
// Behind the scenes:
const controller = new GeminiAIController(GEMINI_API_KEY, API_BASE);
await controller.start(); // Polling setiap 10 detik
```

### Stopping AI Automation

Klik tombol **"⏹️ Stop AI"** untuk menghentikan.

```javascript
controller.stop();
```

### Monitoring Statistics

Klik **"📊 Refresh Stats"** untuk melihat:
- Total keputusan yang dibuat
- Success rate
- Jumlah pump actions
- Jumlah servo actions
- Last decision yang dieksekusi

### Adjusting Poll Interval

Gunakan buttons untuk mengubah frekuensi polling:
- **5s** - Polling setiap 5 detik (lebih responsif, lebih banyak API calls)
- **10s** - Default (balance antara responsif dan efficiency)
- **15s** - Polling setiap 15 detik
- **30s** - Polling setiap 30 detik (lebih hemat bandwidth)

---

## API Endpoints

### GET /ai/status

Fetch status lengkap sistem untuk AI decision making.

```bash
curl http://192.168.137.1:5000/api/ai/status
```

**Response**:
```json
{
  "system": {
    "timestamp": "2025-11-26T14:30:45",
    "status": "operational",
    "mqtt": "connected"
  },
  "sensors": {
    "temperature": {
      "value": 28.5,
      "unit": "°C",
      "status": "normal"
    },
    "humidity": {
      "value": 65.2,
      "unit": "%",
      "status": "normal"
    },
    "soil_moisture": {
      "value": 35.0,
      "unit": "%",
      "status": "dry"
    },
    "light": {
      "value": 1200,
      "unit": "lux",
      "status": "normal"
    },
    "ph": {
      "value": 6.8,
      "unit": "pH",
      "status": "normal"
    }
  },
  "actuators": {
    "pump": {
      "state": "ON",
      "mode": "auto"
    },
    "servo": {
      "angle": 90,
      "state": "open"
    }
  },
  "recommendations": [
    "⚠️ Tanah kering (35.0%). Pompa air harus aktif untuk irigasi.",
    "✅ Suhu dan kelembaban optimal untuk pertumbuhan tanaman."
  ]
}
```

### POST /ai/control

Kirim perintah kontrol dengan penjelasan (reasoning).

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

**Response**:
```json
{
  "status": "success",
  "action": "pump",
  "command": "on",
  "result": "Pompa diatur ke ON",
  "previous_state": {
    "pump": "OFF",
    "servo_angle": 0
  },
  "new_state": {
    "pump": "ON",
    "reason": "Soil moisture 35%, below 40% threshold"
  },
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45"
}
```

---

## Examples

### Example 1: Automatic Pump Control Based on Soil Moisture

**Scenario**: Tanah kering, AI memutuskan nyalakan pompa

```
1. AI checks /ai/status
   - soil_moisture: 35% (status: "dry")
   - pump: "OFF"

2. Gemini makes decision:
   {
     "action": "pump",
     "command": "on",
     "reason": "Soil moisture 35%, below 40% threshold"
   }

3. AI executes via /ai/control
   - Request sent to ESP32 via MQTT
   - Pump relay GPIO 13 turns HIGH
   
4. Status updated:
   - previous_state: pump OFF
   - new_state: pump ON
   - logged with timestamp
```

### Example 2: Automatic Lid Opening for Cooling

**Scenario**: Suhu tinggi, AI membuka lid untuk pendinginan

```
1. AI checks /ai/status
   - temperature: 32.5°C (status: "critical")
   - servo_angle: 0 (closed)

2. Gemini makes decision:
   {
     "action": "servo",
     "command": "open",
     "value": 90,
     "reason": "Temperature 32.5°C, open lid for cooling"
   }

3. AI executes via /ai/control
   - Request sent to ESP32 via MQTT
   - Servo PWM pins 27 & 14 move to 90°
   
4. Lid opens, air circulates
   - Temperature akan turun
   - AI will monitor dan adjust if needed
```

### Example 3: Partial Servo Opening

**Scenario**: Perlu ventilasi ringan tanpa mengganggu suhu

```
POST /ai/control
{
  "action": "servo",
  "command": "angle",
  "value": 45,
  "reason": "Partial opening for ventilation without excessive heat loss"
}

Response: Servo moves to 45° (partial lid opening)
```

---

## Monitoring & Debugging

### Check AI Status in Console

Buka Developer Tools (F12) → Console untuk melihat logs:

```javascript
[GEMINI-AI] Controller initialized
[STATUS] Retrieved: {...}
[GEMINI] Raw response: {...}
[DECISION] AI Decision: {action: "pump", command: "on", ...}
[EXECUTE] Result: {status: "success", ...}
[LOG] Decision #1: {...}
```

### View Decision Log

```javascript
// Di browser console:
aiController.getLog()

// Output:
[
  {
    timestamp: "2025-11-26T14:30:45",
    decision: {action: "pump", command: "on", ...},
    result: {status: "success", ...},
    status: "success"
  },
  ...
]
```

### Get Statistics

```javascript
aiController.getStats()

// Output:
{
  total_decisions: 12,
  successful: 11,
  failed: 1,
  success_rate: "91.67%",
  pump_actions: 5,
  servo_actions: 4,
  last_decision: {...},
  last_status: {...}
}
```

---

## Troubleshooting

### Issue: "API Key not found"

**Cause**: GEMINI_API_KEY belum di-set di App.jsx

**Solution**:
```javascript
// App.jsx - ganti ini:
const GEMINI_API_KEY = "YOUR_API_KEY_HERE";

// Dengan API Key yang sebenarnya:
const GEMINI_API_KEY = "AIza...xxxxxxxx";
```

### Issue: "MQTT client not initialized"

**Cause**: Backend tidak terhubung ke MQTT broker

**Solution**:
1. Pastikan mosquitto running di `192.168.137.1:1883`
2. Check backend logs: `GET /health`
3. Restart backend service

### Issue: Pompa tidak nyala meskipun soil kering

**Cause**: 
- MQTT communication error
- Relay tidak terhubung dengan benar
- ESP32 tidak menerima command

**Debug**:
1. Check `/api/ai/status` - verify soil_moisture value
2. Check `/health` - verify MQTT connected
3. Lihat console logs - check Gemini decision
4. Verify MQTT messages sampai ESP32
5. Test relay manually dengan `/api/control`

### Issue: Servo tidak bergerak

**Cause**:
- PWM pins tidak terhubung
- Servo power supply issue
- ESP32 PWM tidak berfungsi

**Debug**:
1. Check servo angle di `/api/ai/status`
2. Lihat servo logs di ESP32 console
3. Test servo dengan direct angle command:
   ```bash
   curl -X POST http://192.168.137.1:5000/api/ai/control \
     -H "Content-Type: application/json" \
     -d '{
       "action": "servo",
       "command": "angle",
       "value": 90
     }'
   ```

### Issue: High API latency / Slow response

**Cause**: Poll interval terlalu cepat, banyak API calls

**Solution**: Increase poll interval
```javascript
controller.setPollInterval(30000); // 30 detik
```

### Issue: Gemini API Error 429 (Too many requests)

**Cause**: Rate limiting dari Google API

**Solution**: Increase poll interval atau disable AI sementara

---

## Performance Optimization

### 1. Adjust Poll Interval

```javascript
// Fast response (gunakan untuk testing)
controller.setPollInterval(5000);  // 5 detik

// Balanced (default)
controller.setPollInterval(10000); // 10 detik

// Energy efficient
controller.setPollInterval(30000); // 30 detik
```

### 2. Disable AI when not needed

```javascript
controller.stop(); // Stop polling
```

### 3. Monitor Resource Usage

Lihat browser DevTools → Performance tab untuk:
- CPU usage
- Memory consumption
- Network bandwidth

---

## Best Practices

### 1. Always Monitor First Decision

Sebelum biarkan AI berjalan fully automatic, monitor dulu:
- Lihat decision yang dibuat
- Verify akurasi
- Check historical logs

### 2. Set Alert Thresholds

Tambahkan notifikasi jika:
- Temperature > 35°C
- Humidity > 90%
- Soil moisture < 25% (emergency)

### 3. Regular Calibration

Update thresholds bulan sekali berdasarkan:
- Plant growth status
- Seasonal changes
- Sensor accuracy

### 4. Backup Manual Control

Selalu ada tombol manual untuk:
- Override AI decisions
- Emergency stop pump
- Direct servo control

---

## Advanced Features

### Custom Decision Logic

Edit `GeminiAIController.js` method `buildContext()` untuk:
- Customize thresholds
- Add seasonal rules
- Implement plant-specific logic

```javascript
buildContext(status) {
  const sensors = status.sensors;
  
  // Custom logic untuk musim panas
  const SUMMER_TEMP_THRESHOLD = 32;
  const WINTER_TEMP_THRESHOLD = 18;
  
  // Custom soil moisture
  const VERY_DRY_THRESHOLD = 25;
  const VERY_WET_THRESHOLD = 85;
  
  // ... build prompt dengan custom logic
}
```

### Integration dengan Third-party Systems

```javascript
// Log ke cloud service
async function logDecision(decision, result) {
  await fetch('https://your-cloud-api.com/log', {
    method: 'POST',
    body: JSON.stringify({decision, result})
  });
}

// Send alert via Telegram/Email
async function sendAlert(message) {
  await fetch('https://your-notification-service.com/send', {
    method: 'POST',
    body: JSON.stringify({message})
  });
}
```

---

## Changelog

### v1.0.0 (2025-11-26)
- ✅ Initial Gemini AI integration
- ✅ Automatic pump control based on soil moisture
- ✅ Servo control for temperature management
- ✅ Decision logging and statistics
- ✅ Frontend UI with start/stop controls
- ✅ Customizable poll intervals

---

## Support & Documentation

- **API Documentation**: `/backend/AI_CONTROL_ENDPOINTS.md`
- **GeminiAI Class**: `/frontend/src/GeminiAIController.js`
- **Main App**: `/frontend/src/App.jsx`

---

**Status**: Production Ready ✅  
**Last Updated**: 2025-11-26  
**Maintained By**: IoT Development Team
