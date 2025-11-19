from flask import Flask
from flask_cors import CORS
from database.db_init import init_db, get_session
from mqtt_handler import MQTTClient
from routes.api import api_bp
from database.models import Sensor, Measurement

# Global MQTT client
mqtt_client = None

def get_or_create_sensor(session, name, location):
    """Helper to get or create sensor"""
    sensor = session.query(Sensor).filter_by(name=name, location=location).first()
    if not sensor:
        sensor = Sensor(name=name, location=location)
        session.add(sensor)
        session.commit()
    return sensor

def on_mqtt_message(topic, data):
    """Callback when MQTT message received from ESP32"""
    print(f"[MQTT] {topic}: {data}")
    
    session = get_session()
    try:
        if isinstance(data, dict):
            # Temperature
            if 'temperature_c' in data and data['temperature_c'] is not None:
                sensor = get_or_create_sensor(session, 'DHT22_TEMP', 'Chili Plant')
                m = Measurement(sensor_id=sensor.id, value=data['temperature_c'], unit='C')
                session.add(m)
            
            # Humidity
            if 'humidity_pct' in data and data['humidity_pct'] is not None:
                sensor = get_or_create_sensor(session, 'DHT22_HUMIDITY', 'Chili Plant')
                m = Measurement(sensor_id=sensor.id, value=data['humidity_pct'], unit='%')
                session.add(m)
            
            # Soil moisture
            if 'soil_moisture' in data and data['soil_moisture'] is not None:
                sensor = get_or_create_sensor(session, 'SOIL_MOISTURE', 'Chili Plant')
                m = Measurement(sensor_id=sensor.id, value=data['soil_moisture'], unit='%')
                session.add(m)
            
            # pH
            if 'ph' in data and data['ph'] is not None:
                sensor = get_or_create_sensor(session, 'PH_SENSOR', 'Chili Plant')
                m = Measurement(sensor_id=sensor.id, value=data['ph'], unit='pH')
                session.add(m)
            
            # Light (check both light_lux and lux for compatibility)
            light_value = data.get('light_lux') or data.get('lux')
            if light_value is not None:
                sensor = get_or_create_sensor(session, 'BH1750', 'Chili Plant')
                m = Measurement(sensor_id=sensor.id, value=light_value, unit='lux')
                session.add(m)
            
            session.commit()
    except Exception as e:
        print(f"[ERROR] Saving data: {e}")
        session.rollback()
    finally:
        session.close()

def create_app():
    global mqtt_client
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Enable CORS for monorepo frontend
    CORS(app)

    # Initialize database
    init_db()

    # Initialize MQTT client
    mqtt_client = MQTTClient(
        broker=app.config['MQTT_BROKER'],
        port=app.config['MQTT_PORT'],
        topic=app.config['MQTT_SENSOR_TOPIC'],
        on_message_cb=on_mqtt_message
    )
    try:
        mqtt_client.connect()
        print(f"[OK] MQTT connected to {app.config['MQTT_BROKER']}:{app.config['MQTT_PORT']}")
    except Exception as e:
        print(f"[WARN] MQTT connection failed: {e}")

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Store mqtt_client in app context
    app.mqtt_client = mqtt_client

    return app

if __name__ == '__main__':
    app = create_app()
    # Run on hotspot IP for cross-device access (192.168.137.1)
    app.run(host='192.168.137.1', port=5000, debug=False)
