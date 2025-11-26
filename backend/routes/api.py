"""
REST API Endpoints untuk IoT Chili Garden Backend
Partner dapat fetch data melalui endpoints ini
"""
from flask import Blueprint, jsonify, request, current_app
import json
from database.db_init import get_session
from database.models import Sensor, Measurement
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

# ============================================================================
# SENSOR ENDPOINTS
# ============================================================================

@api_bp.route('/sensors', methods=['GET'])
def get_sensors():
    """Get all sensors
    
    Returns:
        [
            {
                "id": 1,
                "name": "DHT22_TEMP",
                "location": "Chili Plant"
            },
            ...
        ]
    """
    session = get_session()
    try:
        sensors = session.query(Sensor).all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'location': s.location
        } for s in sensors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@api_bp.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """Get specific sensor by ID
    
    Returns:
        {
            "id": 1,
            "name": "DHT22_TEMP",
            "location": "Chili Plant"
        }
    """
    session = get_session()
    try:
        sensor = session.query(Sensor).filter_by(id=sensor_id).first()
        if not sensor:
            return jsonify({'error': 'Sensor not found'}), 404
        return jsonify({
            'id': sensor.id,
            'name': sensor.name,
            'location': sensor.location
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# ============================================================================
# MEASUREMENT ENDPOINTS
# ============================================================================

@api_bp.route('/measurements', methods=['GET'])
def get_measurements():
    """Get all measurements (with optional filters)
    
    Query Parameters:
        - sensor_id: Filter by sensor ID
        - limit: Max results (default: 100)
        - hours: Data from last N hours (default: 24)
    
    Returns:
        [
            {
                "id": 1,
                "sensor_id": 1,
                "sensor_name": "DHT22_TEMP",
                "value": 28.5,
                "unit": "C",
                "timestamp": "2025-11-18T10:30:45"
            },
            ...
        ]
    """
    session = get_session()
    try:
        sensor_id = request.args.get('sensor_id', type=int)
        limit = request.args.get('limit', default=100, type=int)
        hours = request.args.get('hours', default=24, type=int)
        
        query = session.query(Measurement)
        
        # Filter by sensor if provided
        if sensor_id:
            query = query.filter_by(sensor_id=sensor_id)
        
        # Filter by time
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Measurement.timestamp >= time_threshold)
        
        # Order and limit
        measurements = query.order_by(Measurement.timestamp.desc()).limit(limit).all()
        
        result = []
        for m in measurements:
            sensor = session.query(Sensor).filter_by(id=m.sensor_id).first()
            result.append({
                'id': m.id,
                'sensor_id': m.sensor_id,
                'sensor_name': sensor.name if sensor else 'Unknown',
                'value': m.value,
                'unit': m.unit,
                'timestamp': m.timestamp.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@api_bp.route('/measurements/<int:sensor_id>/latest', methods=['GET'])
def get_latest_measurement(sensor_id):
    """Get latest measurement for a specific sensor
    
    Returns:
        {
            "id": 1,
            "sensor_id": 1,
            "sensor_name": "DHT22_TEMP",
            "value": 28.5,
            "unit": "C",
            "timestamp": "2025-11-18T10:30:45"
        }
    """
    session = get_session()
    try:
        measurement = session.query(Measurement)\
            .filter_by(sensor_id=sensor_id)\
            .order_by(Measurement.timestamp.desc())\
            .first()
        
        if not measurement:
            return jsonify({'error': 'No measurements found'}), 404
        
        sensor = session.query(Sensor).filter_by(id=sensor_id).first()
        
        return jsonify({
            'id': measurement.id,
            'sensor_id': measurement.sensor_id,
            'sensor_name': sensor.name if sensor else 'Unknown',
            'value': measurement.value,
            'unit': measurement.unit,
            'timestamp': measurement.timestamp.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@api_bp.route('/measurements/sensor/<int:sensor_id>', methods=['GET'])
def get_sensor_measurements(sensor_id):
    """Get all measurements for a sensor
    
    Query Parameters:
        - limit: Max results (default: 100)
        - hours: Data from last N hours (default: 24)
        - order: 'asc' or 'desc' (default: 'desc')
    
    Returns:
        [
            {
                "id": 1,
                "value": 28.5,
                "unit": "C",
                "timestamp": "2025-11-18T10:30:45"
            },
            ...
        ]
    """
    session = get_session()
    try:
        limit = request.args.get('limit', default=100, type=int)
        hours = request.args.get('hours', default=24, type=int)
        order = request.args.get('order', default='desc', type=str).lower()
        
        # Check sensor exists
        sensor = session.query(Sensor).filter_by(id=sensor_id).first()
        if not sensor:
            return jsonify({'error': 'Sensor not found'}), 404
        
        # Get measurements
        query = session.query(Measurement).filter_by(sensor_id=sensor_id)
        
        # Filter by time
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Measurement.timestamp >= time_threshold)
        
        # Order
        if order == 'asc':
            query = query.order_by(Measurement.timestamp.asc())
        else:
            query = query.order_by(Measurement.timestamp.desc())
        
        measurements = query.limit(limit).all()
        
        result = [{
            'id': m.id,
            'value': m.value,
            'unit': m.unit,
            'timestamp': m.timestamp.isoformat()
        } for m in measurements]
        
        return jsonify({
            'sensor_id': sensor_id,
            'sensor_name': sensor.name,
            'sensor_location': sensor.location,
            'count': len(result),
            'measurements': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# ============================================================================
# DATA SUMMARY ENDPOINTS
# ============================================================================

@api_bp.route('/data/latest', methods=['GET'])
def get_latest_data():
    """Get latest reading from all sensors in flat format for frontend
    
    Returns:
        {
            "temperature_c": 28.5,
            "humidity_pct": 65.0,
            "soil_moisture": 55,
            "ph": 6.8,
            "light_lux": 1250.0,
            "timestamp": "2025-11-18T10:30:45"
        }
    """
    session = get_session()
    try:
        sensors = session.query(Sensor).all()
        
        result = {
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Mapping nama sensor ke field name untuk frontend
        sensor_field_map = {
            'DHT22_TEMP': 'temperature_c',
            'DHT22_HUMIDITY': 'humidity_pct',
            'SOIL_MOISTURE': 'soil_moisture',
            'PH_SENSOR': 'ph',
            'BH1750': 'light_lux'
        }
        
        for sensor in sensors:
            latest = session.query(Measurement)\
                .filter_by(sensor_id=sensor.id)\
                .order_by(Measurement.timestamp.desc())\
                .first()
            
            if latest:
                field_name = sensor_field_map.get(sensor.name, sensor.name.lower())
                result[field_name] = latest.value
                # Also store timestamp from latest measurement
                if 'timestamp' not in result or latest.timestamp.isoformat() > result.get('timestamp', ''):
                    result['timestamp'] = latest.timestamp.isoformat()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@api_bp.route('/data/average', methods=['GET'])
def get_average_data():
    """Get average values for all sensors (last 24 hours)
    
    Query Parameters:
        - hours: Calculate average for last N hours (default: 24)
        - sensor_id: Specific sensor (optional)
    
    Returns:
        {
            "period_hours": 24,
            "sensors": {
                "DHT22_TEMP": {
                    "average": 27.3,
                    "min": 25.0,
                    "max": 30.5,
                    "unit": "C"
                },
                ...
            }
        }
    """
    session = get_session()
    try:
        hours = request.args.get('hours', default=24, type=int)
        sensor_id = request.args.get('sensor_id', type=int)
        
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        sensors = session.query(Sensor).all()
        if sensor_id:
            sensors = [s for s in sensors if s.id == sensor_id]
        
        result = {
            'period_hours': hours,
            'sensors': {}
        }
        
        for sensor in sensors:
            measurements = session.query(Measurement)\
                .filter_by(sensor_id=sensor.id)\
                .filter(Measurement.timestamp >= time_threshold)\
                .all()
            
            if measurements:
                values = [m.value for m in measurements]
                result['sensors'][sensor.name] = {
                    'location': sensor.location,
                    'average': round(sum(values) / len(values), 2),
                    'min': min(values),
                    'max': max(values),
                    'count': len(measurements),
                    'unit': measurements[0].unit
                }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================

@api_bp.route('/control', methods=['POST'])
def control_device():
    """Send control command to ESP32 via MQTT with relay validation
    
    Request Body:
        {
            "pump": "on|off|auto",      # Relay control
            "servo": 0-180,              # Servo angle
            "auto": true|false           # Auto mode toggle
        }
    
    Returns:
        {
            "status": "ok",
            "message": "Command sent",
            "timestamp": "2025-11-18T10:30:45",
            "command": {...}
        }
    """
    data = request.get_json() or {}
    
    if not data:
        return jsonify({
            'error': 'No data provided',
            'status': 'failed'
        }), 400
    
    mqtt_client = current_app.mqtt_client
    if not mqtt_client:
        return jsonify({
            'error': 'MQTT not initialized',
            'status': 'failed'
        }), 500
    
    # Validate pump command if provided
    if 'pump' in data:
        valid_pump_cmds = ['on', 'off', 'auto']
        if data['pump'] not in valid_pump_cmds:
            return jsonify({
                'error': f"Invalid pump command. Valid: {valid_pump_cmds}",
                'status': 'failed'
            }), 400
    
    # Validate servo angle if provided
    if 'servo' in data:
        servo_angle = data['servo']
        if not isinstance(servo_angle, (int, float)) or servo_angle < 0 or servo_angle > 180:
            return jsonify({
                'error': 'Servo angle must be 0-180',
                'status': 'failed'
            }), 400
    
    try:
        topic = current_app.config['MQTT_COMMAND_TOPIC']
        payload = json.dumps(data)
        mqtt_client.publish(topic, payload)
        
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        
        print(f"[API-RELAY] Control command published to {topic}")
        print(f"[API-RELAY] Pump: {data.get('pump', 'N/A')} | Servo: {data.get('servo', 'N/A')} | Auto: {data.get('auto', 'N/A')}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Command sent to device',
            'timestamp': timestamp,
            'command': data
        }), 200
    except Exception as e:
        print(f"[API-RELAY] Error publishing command: {str(e)}")
        return jsonify({
            'error': f'Failed to send command: {str(e)}',
            'status': 'failed'
        }), 500

@api_bp.route('/actuator/status', methods=['GET'])
def get_actuator_status():
    """Get current actuator status (pump relay, servo)
    
    Returns:
        {
            "pump": "ON|OFF|UNKNOWN",
            "servo_angle": 0-180,
            "auto_mode": false,
            "relay_pin": 26
        }
    """
    try:
        # Get status from app's in-memory state (updated by MQTT callback)
        pump_state = current_app.config.get('PUMP_STATE', 'UNKNOWN')
        relay_pin = current_app.config.get('RELAY_PIN', 26)
        
        return jsonify({
            'pump': pump_state,
            'servo_angle': 0,
            'auto_mode': False,
            'relay_pin': relay_pin
        }), 200
    except Exception as e:
        print(f"[ERROR] /actuator/status: {e}")
        return jsonify({
            'pump': 'UNKNOWN',
            'servo_angle': 0,
            'auto_mode': False,
            'relay_pin': 26
        }), 200

# ============================================================================
# AI ENDPOINTS (untuk Gemini API)
# ============================================================================

@api_bp.route('/ai/status', methods=['GET'])
def ai_get_status():
    """AI-friendly endpoint untuk mendapatkan status sistem lengkap
    
    Endpoint ini dioptimalkan untuk dikonsumsi oleh AI/Gemini API
    untuk membuat keputusan automasi secara real-time.
    
    Returns:
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
                    "status": "normal|warning|critical"
                },
                "humidity": {
                    "value": 65.2,
                    "unit": "%",
                    "status": "normal|warning|critical"
                },
                "soil_moisture": {
                    "value": 45.0,
                    "unit": "%",
                    "status": "dry|normal|wet"
                },
                "light": {
                    "value": 1200,
                    "unit": "lux",
                    "status": "normal|warning|critical"
                },
                "ph": {
                    "value": 6.8,
                    "unit": "pH",
                    "status": "normal|warning|critical"
                }
            },
            "actuators": {
                "pump": {
                    "state": "ON|OFF",
                    "mode": "auto|manual"
                },
                "servo": {
                    "angle": 90,
                    "state": "open|closed"
                }
            },
            "recommendations": [
                "Pompa air sedang aktif karena tanah kering",
                "Cahaya cukup untuk pertumbuhan optimal"
            ]
        }
    """
    session = get_session()
    try:
        # Get latest sensor readings
        from sqlalchemy import desc
        
        temp = session.query(Measurement).join(Sensor).filter(
            Sensor.name == 'DHT22_TEMP'
        ).order_by(desc(Measurement.timestamp)).first()
        
        humidity = session.query(Measurement).join(Sensor).filter(
            Sensor.name == 'DHT22_HUMIDITY'
        ).order_by(desc(Measurement.timestamp)).first()
        
        soil = session.query(Measurement).join(Sensor).filter(
            Sensor.name == 'SOIL_MOISTURE'
        ).order_by(desc(Measurement.timestamp)).first()
        
        light = session.query(Measurement).join(Sensor).filter(
            Sensor.name == 'BH1750'
        ).order_by(desc(Measurement.timestamp)).first()
        
        ph = session.query(Measurement).join(Sensor).filter(
            Sensor.name == 'PH_SENSOR'
        ).order_by(desc(Measurement.timestamp)).first()
        
        # Determine sensor status
        def get_temp_status(val):
            if val is None: return "unknown"
            if 20 <= val <= 30: return "normal"
            if val < 15 or val > 35: return "critical"
            return "warning"
        
        def get_humidity_status(val):
            if val is None: return "unknown"
            if 60 <= val <= 85: return "normal"
            if val < 40 or val > 95: return "critical"
            return "warning"
        
        def get_soil_status(val):
            if val is None: return "unknown"
            if val < 30: return "dry"
            if val < 40: return "warning_dry"
            if val > 80: return "wet"
            if val > 70: return "warning_wet"
            return "normal"
        
        def get_light_status(val):
            if val is None: return "unknown"
            if val < 500: return "critical"
            if val < 1000: return "warning"
            if val > 10000: return "warning"
            return "normal"
        
        def get_ph_status(val):
            if val is None: return "unknown"
            if 6.0 <= val <= 7.5: return "normal"
            if val < 5.5 or val > 8.0: return "critical"
            return "warning"
        
        temp_val = temp.value if temp else None
        humidity_val = humidity.value if humidity else None
        soil_val = soil.value if soil else None
        light_val = light.value if light else None
        ph_val = ph.value if ph else None
        
        # Get actuator status
        pump_state = current_app.config.get('PUMP_STATE', 'OFF')
        servo_angle = current_app.config.get('SERVO_ANGLE', 0)
        
        # Generate recommendations
        recommendations = []
        if soil_val is not None:
            if soil_val < 40:
                recommendations.append(f"⚠️ Tanah kering ({soil_val:.1f}%). Pompa air harus aktif untuk irigasi.")
            elif soil_val > 75:
                recommendations.append(f"💧 Tanah sangat basah ({soil_val:.1f}%). Pertimbangkan matikan pompa.")
        
        if temp_val is not None:
            if temp_val > 32:
                recommendations.append(f"🌡️ Suhu tinggi ({temp_val:.1f}°C). Tingkatkan ventilasi atau penyiraman.")
            elif temp_val < 18:
                recommendations.append(f"❄️ Suhu rendah ({temp_val:.1f}°C). Pertimbangkan penghangatan.")
        
        if light_val is not None:
            if light_val < 500:
                recommendations.append(f"🌑 Cahaya kurang ({light_val:.0f} lux). Tambah pencahayaan atau buka tutup.")
        
        if humidity_val is not None:
            if humidity_val > 85:
                recommendations.append(f"💨 Kelembaban tinggi ({humidity_val:.1f}%). Tingkatkan sirkulasi udara.")
        
        if not recommendations:
            recommendations.append("✅ Semua kondisi optimal untuk pertumbuhan tanaman.")
        
        return jsonify({
            'system': {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'operational',
                'mqtt': 'connected' if current_app.mqtt_client else 'disconnected'
            },
            'sensors': {
                'temperature': {
                    'value': round(temp_val, 2) if temp_val else None,
                    'unit': '°C',
                    'status': get_temp_status(temp_val)
                },
                'humidity': {
                    'value': round(humidity_val, 2) if humidity_val else None,
                    'unit': '%',
                    'status': get_humidity_status(humidity_val)
                },
                'soil_moisture': {
                    'value': round(soil_val, 2) if soil_val else None,
                    'unit': '%',
                    'status': get_soil_status(soil_val)
                },
                'light': {
                    'value': round(light_val, 2) if light_val else None,
                    'unit': 'lux',
                    'status': get_light_status(light_val)
                },
                'ph': {
                    'value': round(ph_val, 2) if ph_val else None,
                    'unit': 'pH',
                    'status': get_ph_status(ph_val)
                }
            },
            'actuators': {
                'pump': {
                    'state': pump_state,
                    'mode': 'auto'
                },
                'servo': {
                    'angle': servo_angle,
                    'state': 'open' if servo_angle > 45 else 'closed'
                }
            },
            'recommendations': recommendations
        }), 200
    except Exception as e:
        print(f"[ERROR] /ai/status: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
    finally:
        session.close()

@api_bp.route('/ai/control', methods=['POST'])
def ai_control():
    """AI-friendly endpoint untuk kontroling pompa dan servo
    
    Endpoint ini dirancang untuk dikonsumsi oleh Gemini AI yang akan
    membuat keputusan berdasarkan kondisi sensor dan merangsang aktuator.
    
    Request Body:
        {
            "action": "pump|servo",
            "command": "on|off|open|close|angle",
            "value": 90,              # untuk servo angle (0-180)
            "reason": "Tanah kering, perlu irigasi",  # optional explanation
            "auto_triggered": true    # apakah triggered oleh automation
        }
    
    Example:
        1. Pompa ON otomatis:
           POST /ai/control
           {
               "action": "pump",
               "command": "on",
               "reason": "Soil moisture 35%, below 40% threshold",
               "auto_triggered": true
           }
        
        2. Servo terbuka:
           POST /ai/control
           {
               "action": "servo",
               "command": "open",
               "value": 90,
               "reason": "Temperature 32°C, open lid for cooling",
               "auto_triggered": true
           }
        
        3. Servo angle spesifik:
           POST /ai/control
           {
               "action": "servo",
               "command": "angle",
               "value": 45,
               "reason": "Partial opening for ventilation",
               "auto_triggered": true
           }
    
    Returns:
        {
            "status": "success|failed",
            "action": "pump|servo",
            "command": "on|off|open|close",
            "result": "Command executed successfully",
            "previous_state": {...},
            "new_state": {...},
            "timestamp": "2025-11-26T14:30:45"
        }
    """
    data = request.get_json() or {}
    
    # Validation
    if not data:
        return jsonify({
            'status': 'failed',
            'error': 'No data provided',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    action = data.get('action', '').lower()
    command = data.get('command', '').lower()
    value = data.get('value')
    reason = data.get('reason', 'AI Decision')
    auto_triggered = data.get('auto_triggered', False)
    
    # Validate action
    if action not in ['pump', 'servo']:
        return jsonify({
            'status': 'failed',
            'error': f"Invalid action '{action}'. Valid: pump, servo",
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    mqtt_client = current_app.mqtt_client
    if not mqtt_client:
        return jsonify({
            'status': 'failed',
            'error': 'MQTT client not initialized',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    try:
        # Get previous state
        prev_pump_state = current_app.config.get('PUMP_STATE', 'OFF')
        prev_servo_angle = current_app.config.get('SERVO_ANGLE', 0)
        
        # Build MQTT payload
        mqtt_payload = {}
        result_message = ""
        new_state = {}
        
        if action == 'pump':
            # Validate pump command
            if command not in ['on', 'off']:
                return jsonify({
                    'status': 'failed',
                    'error': f"Invalid pump command '{command}'. Valid: on, off",
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            mqtt_payload = {'pump': command}
            result_message = f"Pompa diatur ke {command.upper()}"
            new_state = {'pump': command.upper(), 'reason': reason}
        
        elif action == 'servo':
            # Validate servo command
            if command == 'open':
                servo_val = 90
                mqtt_payload = {'servo': servo_val}
                result_message = f"Servo dibuka (90°)"
            elif command == 'close':
                servo_val = 0
                mqtt_payload = {'servo': servo_val}
                result_message = f"Servo ditutup (0°)"
            elif command == 'angle':
                servo_val = value
                if servo_val is None or not isinstance(servo_val, (int, float)) or servo_val < 0 or servo_val > 180:
                    return jsonify({
                        'status': 'failed',
                        'error': 'Servo angle must be 0-180',
                        'timestamp': datetime.utcnow().isoformat()
                    }), 400
                mqtt_payload = {'servo': servo_val}
                result_message = f"Servo diatur ke {servo_val}°"
            else:
                return jsonify({
                    'status': 'failed',
                    'error': f"Invalid servo command '{command}'. Valid: open, close, angle",
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            new_state = {'servo_angle': servo_val, 'reason': reason}
        
        # Publish to MQTT
        topic = current_app.config.get('MQTT_COMMAND_TOPIC', 'esp32/chili/cmd')
        mqtt_client.publish(topic, json.dumps(mqtt_payload))
        
        # Log the AI action
        trigger_type = "AUTO-AI" if auto_triggered else "MANUAL-AI"
        print(f"[{trigger_type}] Action: {action} | Command: {command} | Reason: {reason}")
        
        return jsonify({
            'status': 'success',
            'action': action,
            'command': command,
            'result': result_message,
            'previous_state': {
                'pump': prev_pump_state,
                'servo_angle': prev_servo_angle
            },
            'new_state': new_state,
            'reason': reason,
            'auto_triggered': auto_triggered,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        print(f"[ERROR] /ai/control: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint
    
    Returns:
        {
            "status": "ok",
            "timestamp": "2025-11-18T10:30:45",
            "mqtt": "connected|disconnected"
        }
    """
    mqtt_status = "connected" if current_app.mqtt_client else "disconnected"
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'mqtt': mqtt_status,
        'broker': current_app.config['MQTT_BROKER'],
        'port': current_app.config['MQTT_PORT']
    }), 200

@api_bp.route('/info', methods=['GET'])
def info():
    """API information endpoint
    
    Returns info about available endpoints and version
    """
    return jsonify({
        'name': 'IoT Chili Garden Backend API',
        'version': '1.0.0',
        'api_version': 'v1',
        'base_url': '/api',
        'mqtt_broker': current_app.config['MQTT_BROKER'],
        'mqtt_port': current_app.config['MQTT_PORT'],
        'endpoints': {
            'sensors': {
                'GET /sensors': 'Get all sensors',
                'GET /sensors/<id>': 'Get specific sensor'
            },
            'measurements': {
                'GET /measurements': 'Get all measurements (with filters)',
                'GET /measurements/<sensor_id>/latest': 'Get latest reading',
                'GET /measurements/sensor/<sensor_id>': 'Get sensor history'
            },
            'data': {
                'GET /data/latest': 'Get latest from all sensors',
                'GET /data/average': 'Get averages (24 hours)'
            },
            'control': {
                'POST /control': 'Send command to ESP32'
            },
            'ai': {
                'GET /ai/status': 'Get system status for AI (optimized format)',
                'POST /ai/control': 'AI control pump and servo with reasoning'
            },
            'system': {
                'GET /health': 'Health check',
                'GET /info': 'This endpoint'
            }
        }
    }), 200
