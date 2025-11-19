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
    """Send control command to ESP32 via MQTT
    
    Request Body:
        {
            "pump": "on|off|auto",
            "servo": 0-180,
            "auto": true|false
        }
    
    Returns:
        {
            "status": "ok",
            "message": "Command sent",
            "command": {...}
        }
    """
    data = request.get_json() or {}
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    mqtt_client = current_app.mqtt_client
    if not mqtt_client:
        return jsonify({'error': 'MQTT not initialized'}), 500
    
    try:
        topic = current_app.config['MQTT_COMMAND_TOPIC']
        payload = json.dumps(data)
        mqtt_client.publish(topic, payload)
        
        print(f"[API] Published control command: {data}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Command sent to device',
            'command': data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            'system': {
                'GET /health': 'Health check',
                'GET /info': 'This endpoint'
            }
        }
    }), 200
