import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = "AIzaSyAeefoAQX3A6RdjHfj9rYTwvCWdB5UryPA"

    # MQTT settings - use local IP (hotspot)
    MQTT_BROKER = os.environ.get('MQTT_BROKER', '192.168.137.1')
    MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
    MQTT_SENSOR_TOPIC = os.environ.get('MQTT_SENSOR_TOPIC', 'esp32/chili/data')
    MQTT_COMMAND_TOPIC = os.environ.get('MQTT_COMMAND_TOPIC', 'esp32/chili/cmd')
