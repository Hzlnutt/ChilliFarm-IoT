# AI Control Endpoints Documentation

## Overview

Sistem IoT Chili Garden menyediakan dua endpoint khusus yang dioptimalkan untuk konsumsi oleh **Gemini AI** atau sistem AI lainnya. Endpoint ini dirancang untuk memberikan informasi status lengkap dan memungkinkan kontrol otomatis pompa air dan servo berdasarkan keputusan AI.

**Base URL**: `http://192.168.137.1:5000/api`

---

## 1. GET /ai/status

### Tujuan
Mengambil status lengkap sistem dalam format yang mudah dipahami oleh AI untuk membuat keputusan automasi.

### Request
```http
GET /api/ai/status
```

### Response (200 OK)
```json
{
  "system": {
    "timestamp": "2025-11-26T14:30:45.123456",
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

### Status Explanation

#### Sensor Status
- **temperature**: `normal | warning | critical`
  - normal: 20-30°C
  - warning: 15-20°C, 30-35°C
  - critical: <15°C, >35°C

- **humidity**: `normal | warning | critical`
  - normal: 60-85%
  - warning: 40-60%, 85-95%
  - critical: <40%, >95%

- **soil_moisture**: `dry | warning_dry | normal | warning_wet | wet | unknown`
  - dry: <30%
  - warning_dry: 30-40%
  - normal: 40-70%
  - warning_wet: 70-80%
  - wet: >80%

- **light**: `normal | warning | critical`
  - normal: 1000-10000 lux
  - warning: 500-1000 lux, >10000 lux
  - critical: <500 lux

- **ph**: `normal | warning | critical`
  - normal: 6.0-7.5
  - warning: 5.5-6.0, 7.5-8.0
  - critical: <5.5, >8.0

#### Actuator State
- **pump.state**: `ON | OFF | UNKNOWN`
- **servo.angle**: `0-180` (0=closed, 90=open)
- **servo.state**: `open | closed` (derived from angle)

### Contoh Penggunaan
```bash
curl -X GET "http://192.168.137.1:5000/api/ai/status" \
  -H "Accept: application/json"
```

---

## 2. POST /ai/control

### Tujuan
Mengirim perintah kontrol pompa atau servo melalui AI dengan penjelasan alasan keputusan.

### Request
```http
POST /api/ai/control
Content-Type: application/json

{
  "action": "pump|servo",
  "command": "on|off|open|close|angle",
  "value": 90,
  "reason": "Tanah kering, perlu irigasi",
  "auto_triggered": true
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✅ Yes | `pump` atau `servo` |
| `command` | string | ✅ Yes | Lihat tabel command di bawah |
| `value` | number | ❌ No | Hanya untuk `servo angle` (0-180) |
| `reason` | string | ❌ No | Penjelasan mengapa AI membuat keputusan ini |
| `auto_triggered` | boolean | ❌ No | `true` jika triggered otomatis, `false` jika manual (default: false) |

### Command Reference

#### Pump Commands
| Command | Description | Value Required |
|---------|-------------|-----------------|
| `on` | Nyalakan pompa air | ❌ No |
| `off` | Matikan pompa air | ❌ No |

#### Servo Commands
| Command | Description | Value Required |
|---------|-------------|-----------------|
| `open` | Buka servo (90°) | ❌ No |
| `close` | Tutup servo (0°) | ❌ No |
| `angle` | Set servo ke angle spesifik | ✅ Yes (0-180) |

### Response (200 OK - Success)
```json
{
  "status": "success",
  "action": "pump",
  "command": "on",
  "result": "Pompa diatur ke ON",
  "previous_state": {
    "pump": "OFF",
    "servo_angle": 45
  },
  "new_state": {
    "pump": "ON",
    "reason": "Tanah kering, perlu irigasi"
  },
  "reason": "Tanah kering, perlu irigasi",
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45.123456"
}
```

### Response (400/500 Error)
```json
{
  "status": "failed",
  "error": "Invalid pump command 'invalid'. Valid: on, off",
  "timestamp": "2025-11-26T14:30:45.123456"
}
```

### Error Handling

| Status Code | Condition |
|------------|-----------|
| `200` | Perintah berhasil dieksekusi |
| `400` | Invalid request (action/command/value tidak valid) |
| `500` | Server error atau MQTT tidak terhubung |

---

## Contoh Penggunaan

### 1. Pompa Air ON (Tanah Kering)
```bash
curl -X POST "http://192.168.137.1:5000/api/ai/control" \
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
  "reason": "Soil moisture 35%, below 40% threshold",
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45.123456"
}
```

---

### 2. Servo Buka (Pendinginan)
```bash
curl -X POST "http://192.168.137.1:5000/api/ai/control" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "servo",
    "command": "open",
    "reason": "Temperature 32°C, open lid for cooling",
    "auto_triggered": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "action": "servo",
  "command": "open",
  "result": "Servo dibuka (90°)",
  "previous_state": {
    "pump": "ON",
    "servo_angle": 0
  },
  "new_state": {
    "servo_angle": 90,
    "reason": "Temperature 32°C, open lid for cooling"
  },
  "reason": "Temperature 32°C, open lid for cooling",
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45.123456"
}
```

---

### 3. Servo Angle Spesifik (Ventilasi Partial)
```bash
curl -X POST "http://192.168.137.1:5000/api/ai/control" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "servo",
    "command": "angle",
    "value": 45,
    "reason": "Partial opening for ventilation without excessive heat loss",
    "auto_triggered": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "action": "servo",
  "command": "angle",
  "result": "Servo diatur ke 45°",
  "previous_state": {
    "pump": "ON",
    "servo_angle": 90
  },
  "new_state": {
    "servo_angle": 45,
    "reason": "Partial opening for ventilation without excessive heat loss"
  },
  "reason": "Partial opening for ventilation without excessive heat loss",
  "auto_triggered": true,
  "timestamp": "2025-11-26T14:30:45.123456"
}
```

---

### 4. Pompa OFF (Tanah Basah)
```bash
curl -X POST "http://192.168.137.1:5000/api/ai/control" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "pump",
    "command": "off",
    "reason": "Soil moisture 78%, above 70% threshold",
    "auto_triggered": true
  }'
```

---

## Integration dengan Gemini API

### Setup Gemini API

1. **Dapatkan API Key** dari [Google AI Studio](https://aistudio.google.com/app/apikeys)

2. **Environment Variable** (di frontend):
```javascript
const GEMINI_API_KEY = "YOUR_API_KEY_HERE";
```

### Contoh Integration Flow

```javascript
// 1. Fetch current system status
const response = await fetch('http://192.168.137.1:5000/api/ai/status');
const systemStatus = await response.json();

// 2. Send to Gemini untuk decision making
const geminiResponse = await fetch(
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{
        parts: [{
          text: `Current system status: ${JSON.stringify(systemStatus)}
          
Based on this data, provide a JSON response with:
{
  "action": "pump|servo",
  "command": "on|off|open|close|angle",
  "value": optional_number,
  "reason": "explanation"
}

Only respond with valid JSON, no other text.`
        }]
      }]
    })
  }
);

// 3. Parse Gemini response
const geminiData = await geminiResponse.json();
const decision = JSON.parse(geminiData.candidates[0].content.parts[0].text);

// 4. Execute command via AI control endpoint
const controlResponse = await fetch('http://192.168.137.1:5000/api/ai/control', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ...decision,
    auto_triggered: true
  })
});

const result = await controlResponse.json();
console.log('AI Decision Executed:', result);
```

---

## Best Practices

### 1. Polling Interval
```javascript
// Fetch status setiap 10 detik untuk AI decision making
setInterval(async () => {
  const status = await fetch('http://192.168.137.1:5000/api/ai/status').then(r => r.json());
  // Process dengan Gemini
}, 10000);
```

### 2. Error Handling
```javascript
try {
  const result = await fetch('http://192.168.137.1:5000/api/ai/control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(aiDecision)
  });
  
  if (!result.ok) {
    console.error('Control failed:', await result.json());
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### 3. Logging
```javascript
// Log semua keputusan AI untuk audit trail
console.log(`[AI-DECISION] ${decision.reason}`);
console.log(`[AI-EXECUTION] Action: ${result.action}, Status: ${result.status}`);
```

---

## Troubleshooting

### Issue: "MQTT client not initialized"
**Solution**: Pastikan backend sudah terhubung ke MQTT broker
- Check: `GET /health` endpoint
- Verify MQTT broker berjalan di `192.168.137.1:1883`

### Issue: "Invalid action"
**Solution**: Gunakan hanya `pump` atau `servo`
```json
// ❌ WRONG
{ "action": "relay" }

// ✅ CORRECT
{ "action": "pump" }
```

### Issue: Servo tidak bergerak setelah perintah
**Solution**: Verify servo status di `/ai/status`
- Check `servo.state` dan `servo.angle`
- Pastikan ESP32 menerima command via MQTT

### Issue: Koneksi timeout
**Solution**: Verify network connectivity
```bash
ping 192.168.137.1
```

---

## Response Time

| Endpoint | Expected Response Time |
|----------|------------------------|
| `GET /ai/status` | < 200ms |
| `POST /ai/control` | < 500ms |
| MQTT Execution | < 1s |

---

## Rate Limiting
Tidak ada rate limiting, namun disarankan:
- Max `1 request/second` untuk `/ai/status`
- Max `1 request/5 seconds` untuk `/ai/control` (untuk menghindari command spam)

---

## Changelog

### v1.0.0 (2025-11-26)
- ✅ Initial release
- ✅ Endpoint `/ai/status` untuk sensor dan actuator status
- ✅ Endpoint `/ai/control` untuk pump dan servo control
- ✅ AI-friendly JSON format dengan recommendations
- ✅ Support untuk Gemini API integration

---

## Support

Untuk bantuan atau pertanyaan, silakan hubungi tim development atau buat issue di repository.

**Contact**: team@chillifax.local  
**Documentation**: https://github.com/Hzlnutt/ChilliFarm-IoT
