"""
Test script untuk simulasi MQTT dan API testing
Berguna untuk testing tanpa hardware ESP32 aktual
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_CONTROL = f"{BASE_URL}/api/control"
API_STATUS = f"{BASE_URL}/api/status"

def test_api_control():
    """Test API control endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Control API Endpoint")
    print("="*60)
    
    commands = [
        {"name": "Pump ON", "data": {"pump": "on"}},
        {"name": "Pump OFF", "data": {"pump": "off"}},
        {"name": "Pump AUTO", "data": {"pump": "auto"}},
        {"name": "Servo 45 degrees", "data": {"servo": 45}},
        {"name": "Servo 135 degrees", "data": {"servo": 135}},
        {"name": "Enable Auto Mode", "data": {"auto": True}},
        {"name": "Disable Auto Mode", "data": {"auto": False}},
    ]
    
    for cmd in commands:
        try:
            print(f"\n[{cmd['name']}]")
            print(f"  Request: POST {API_CONTROL}")
            print(f"  Payload: {json.dumps(cmd['data'])}")
            
            response = requests.post(
                API_CONTROL,
                json=cmd['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.json()}")
            
            if response.status_code == 200:
                print(f"  [OK] Command accepted")
            else:
                print(f"  [WARN] Unexpected status code")
                
        except Exception as e:
            print(f"  [ERROR] {e}")

def test_api_status():
    """Test API status endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Sensor Status Endpoint")
    print("="*60)
    
    try:
        print(f"\n[GET Sensor Status]")
        print(f"  Request: GET {API_STATUS}")
        
        response = requests.get(API_STATUS, timeout=5)
        
        print(f"  Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            if data:
                print(f"  [OK] Sensor data available:")
                for sensor_name, sensor_data in data.items():
                    print(f"\n    {sensor_name}:")
                    print(f"      Location: {sensor_data.get('location', 'N/A')}")
                    print(f"      Value: {sensor_data.get('value', 'N/A')}")
                    print(f"      Unit: {sensor_data.get('unit', 'N/A')}")
                    print(f"      Timestamp: {sensor_data.get('timestamp', 'N/A')}")
            else:
                print(f"  [WARN] No sensor data available yet")
                print(f"  (Pastikan ESP32 sudah mengirim data ke MQTT)")
        else:
            print(f"  [ERROR] Failed to get sensor status")
            print(f"  Response: {data}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")

def print_mqtt_info():
    """Print MQTT connection info"""
    print("\n" + "="*60)
    print("MQTT Connection Information")
    print("="*60)
    print("\nBroker: broker.hivemq.com:1883")
    print("\nTopics:")
    print("  - Publish (ESP32 -> Backend): sensors/esp32_chili_01/data")
    print("  - Subscribe (Backend -> ESP32): commands/esp32_chili_01/set")
    print("\nSimulate ESP32 sensor data (using mosquitto):")
    print('  mosquitto_pub -h broker.hivemq.com -t "sensors/esp32_chili_01/data" \\')
    print('    -m \'{"temperature_c":28.5,"humidity_pct":65.0,"soil_raw":350,"ph":6.8,"lux":1250}\'')
    print("\nMonitor backend commands to ESP32:")
    print('  mosquitto_sub -h broker.hivemq.com -t "commands/esp32_chili_01/set"')

def main():
    print("\n" + "#"*60)
    print("# IoT Backend - API Testing")
    print("# Make sure Flask server is running: python app.py")
    print("#"*60)
    
    print_mqtt_info()
    
    # Test API endpoints
    try:
        print("\n" + "="*60)
        print("Checking Flask server at " + BASE_URL)
        print("="*60)
        
        response = requests.get(BASE_URL, timeout=2)
        print(f"[OK] Flask server is running!")
        
    except Exception as e:
        print(f"[ERROR] Cannot connect to Flask server!")
        print(f"Make sure to run: python app.py")
        print(f"Error: {e}")
        return
    
    # Run tests
    test_api_control()
    test_api_status()
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nAccess Web Dashboard:")
    print(f"  {BASE_URL}")

if __name__ == "__main__":
    main()
