"""
Test script untuk validasi setup IoT Backend
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[TEST] IoT Backend Configuration Test")
print("-" * 50)

# Test 1: Config
try:
    from config import Config
    print("[OK] Config module loaded")
    print(f"    MQTT_BROKER: {Config.MQTT_BROKER}")
    print(f"    MQTT_PORT: {Config.MQTT_PORT}")
    print(f"    MQTT_TOPIC: {Config.MQTT_TOPIC}")
except Exception as e:
    print(f"[FAIL] Config error: {e}")
    sys.exit(1)

# Test 2: Database models
try:
    from database.models import Sensor, Measurement, Base
    print("[OK] Database models imported")
except Exception as e:
    print(f"[FAIL] Database models error: {e}")
    sys.exit(1)

# Test 3: MQTT Handler
try:
    from mqtt_handler import MQTTClient
    print("[OK] MQTT handler imported")
except Exception as e:
    print(f"[FAIL] MQTT handler error: {e}")
    sys.exit(1)

# Test 4: Routes
try:
    from routes.api import api_bp
    from routes.dashboard import dashboard_bp
    print("[OK] Routes imported")
except Exception as e:
    print(f"[FAIL] Routes error: {e}")
    sys.exit(1)

# Test 5: Create Flask app
try:
    from app import create_app
    print("[OK] App module imported")
    # NOTE: Don't actually create app here because it will try to connect MQTT
    # app = create_app()
    # print("[OK] Flask app created successfully")
except Exception as e:
    print(f"[FAIL] App creation error: {e}")
    sys.exit(1)

print("-" * 50)
print("[SUCCESS] All imports and configurations OK!")
print("")
print("Next steps:")
print("1. Make sure requirements are installed:")
print("   pip install -r requirements.txt")
print("")
print("2. Run Flask server:")
print("   python app.py")
print("")
print("3. Access dashboard at:")
print("   http://localhost:5000")
