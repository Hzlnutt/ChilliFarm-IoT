# Multi-Actuator System Test Plan

## System Overview
- **Lift Relays**: GPIO 26 (left) + GPIO 25 (right) - synchronized up/down
- **Water Pump**: GPIO 13 - on/off control
- **Servos**: GPIO 27 (left) + GPIO 14 (right) - synchronized lid open/close
- **Safety Limits**:
  * Lift: 30s max runtime, 5s min off time
  * Pump: 60s max runtime, 10s min off time
  * Servo angles: 0-180 degrees

## Test Cases

### 1. Backend API - POST /control

#### Test 1.1: Lift Control
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"lift": "up"}'
# Expected: {"status": "ok", "message": "Command sent to device", ...}
```

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 1.2: Lid Control
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"lid": "open"}'
# Expected: {"status": "ok", "message": "Command sent to device", ...}
```

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 1.3: Pump Control
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"pump": "on"}'
# Expected: {"status": "ok", "message": "Command sent to device", ...}
```

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 1.4: Direct Servo Angle
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"servo": 45}'
# Expected: {"status": "ok", "message": "Command sent to device", ...}
```

**Result**: ✓ / ✗  
**Notes**: 

---

### 2. Backend API - GET /actuator/status

#### Test 2.1: Get All Actuator Status
```bash
curl http://192.168.137.1:5000/api/actuator/status
# Expected: {
#   "lift": "UP|DOWN",
#   "lid": "OPEN|CLOSED",
#   "pump": "ON|OFF",
#   "servo_angle": 0-180,
#   "relay_left": 26,
#   "relay_right": 25,
#   "relay_pump": 13,
#   "timestamp": "...",
#   "status": "operational"
# }
```

**Result**: ✓ / ✗  
**Notes**: 

---

### 3. MQTT Command Flow

#### Test 3.1: MQTT Lift Command
1. Publish to `esp32/chili/cmd`: `{"lift": "up"}`
2. Verify ESP32 receives and processes
3. Verify ESP32 publishes status to `esp32/chili/status`

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 3.2: MQTT Pump Command
1. Publish to `esp32/chili/cmd`: `{"pump": "on"}`
2. Verify ESP32 receives and processes
3. Verify GPIO 13 goes HIGH
4. Verify ESP32 publishes status to `esp32/chili/status`

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 3.3: MQTT Lid Command
1. Publish to `esp32/chili/cmd`: `{"lid": "open"}`
2. Verify both servos move to 90 degrees
3. Verify ESP32 publishes status with servo angles

**Result**: ✓ / ✗  
**Notes**: 

---

### 4. Hardware Verification

#### Test 4.1: Relay Activation
- [ ] GPIO 26 LED lights when lift_up() called
- [ ] GPIO 25 LED lights when lift_up() called
- [ ] GPIO 13 LED lights when pump_on() called
- [ ] All relays off when respective off() called

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 4.2: Servo Synchronization
- [ ] GPIO 27 servo moves to commanded angle
- [ ] GPIO 14 servo moves to same angle simultaneously
- [ ] Both servos synchronized within 50ms
- [ ] No binding or stuttering

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 4.3: Pump Operation
- [ ] Pump relay activates with on command
- [ ] Pump relay deactivates with off command
- [ ] Relay response time < 100ms

**Result**: ✓ / ✗  
**Notes**: 

---

### 5. Automation Logic

#### Test 5.1: Pump Auto-On (Dry Soil)
1. Set soil moisture < 40%
2. Enable AUTO_MODE
3. Verify pump turns on automatically

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 5.2: Pump Auto-Off (Wet Soil)
1. Pump running with auto mode
2. Increase soil moisture > 70%
3. Verify pump turns off automatically

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 5.3: Pump Safety Limit
1. Send pump on command
2. Wait 60+ seconds
3. Verify pump auto-off after 60s max runtime

**Result**: ✓ / ✗  
**Notes**: 

---

### 6. Frontend UI Integration

#### Test 6.1: Control Buttons Exist
- [ ] Lift buttons (NAIK/TURUN) exist
- [ ] Lid buttons (BUKA/TUTUP) exist
- [ ] Pump buttons (NYALA/MATI) exist

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 6.2: Lift Control Works
1. Click "NAIK" button
2. Verify API call to /control with {"lift": "up"}
3. Verify lift state updates in UI
4. Click "TURUN" button
5. Verify API call to /control with {"lift": "down"}

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 6.3: Lid Control Works
1. Click "BUKA" button
2. Verify API call to /control with {"lid": "open"}
3. Verify servo angles = 90 degrees
4. Click "TUTUP" button
5. Verify API call to /control with {"lid": "close"}
6. Verify servo angles = 0 degrees

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 6.4: Pump Control Works
1. Click "NYALA" button
2. Verify API call to /control with {"pump": "on"}
3. Verify pump state updates in UI
4. Click "MATI" button
5. Verify API call to /control with {"pump": "off"}

**Result**: ✓ / ✗  
**Notes**: 

---

### 7. Error Handling

#### Test 7.1: Invalid Lift Command
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"lift": "invalid"}'
# Expected: 400 error with message
```

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 7.2: Invalid Servo Angle
```bash
curl -X POST http://192.168.137.1:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"servo": 999}'
# Expected: 400 error "Servo angle must be 0-180"
```

**Result**: ✓ / ✗  
**Notes**: 

---

#### Test 7.3: MQTT Disconnection
1. Stop mosquitto broker
2. Try to send control command
3. Verify error message about MQTT

**Result**: ✓ / ✗  
**Notes**: 

---

## Integration Checklist

- [ ] ESP32 firmware updated with all 3 relays + 2 servos
- [ ] Backend MQTT callback tracks lift, lid, pump, servo state
- [ ] Backend /control endpoint validates all 4 commands
- [ ] Backend /actuator/status returns pump state
- [ ] Frontend has lift, lid, pump control buttons
- [ ] Frontend displays current actuator status
- [ ] Automation: pump responds to soil moisture
- [ ] Safety: pump enforces max runtime + min off time
- [ ] All compile errors resolved
- [ ] MQTT communication working end-to-end

## Sign-Off

**Tested By**: _______________  
**Date**: _______________  
**Result**: ✓ PASSED / ✗ FAILED  

**Issues Found**:

---

**Notes**:

---
