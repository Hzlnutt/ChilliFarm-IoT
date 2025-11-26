# esp32_garden_mqtt.py
# MicroPython code for ESP32 — Chili pepper plant monitoring + MQTT
# Sensors: DHT22, BH1750 (optional), pH (ADC), Soil Moisture (ADC)
# Actuators: Pump (relay), Servo (valve)
# --- PIN SETUP SESUAI WIRING FISIK ESP32 --- #
# Sensor:
# DHT22 (DATA) -> GPIO 15 (3.3V)
# BH1750 -> SDA=21, SCL=22 (3.3V I2C)
# pH Sensor -> Po -> GPIO 35 (analog input), V+ -> 5V, G -> GND
# Soil Moisture -> GPIO 34 (3.3V analog input)
# Lift Kiri (relay) -> GPIO 26 (digital output, aktif HIGH)
# Lift Kanan (relay) -> GPIO 25 (digital output, aktif HIGH)
# Water Pump (relay) -> GPIO 13 (digital output, aktif HIGH)
# Servo Kiri (lid) -> GPIO 27 (PWM output, 50Hz)
# Servo Kanan (lid) -> GPIO 14 (PWM output, 50Hz)
# Semua GND harus dihubungkan bersama (ESP32, sensor, modul, relay, dll)

# DAYA:
# - ESP32: 5V input (dari USB / adaptor)
# - Sensor pH: 5V (V+), output Po sudah dibatasi ≤ 3.0V, aman ke ADC ESP32
# - Sensor lainnya: 3.3V
# - Pompa/Relay: ambil daya eksternal 5V (jangan dari ESP32 langsung)

# MQTT topics: sensors/<device_id>/data, actuators/<device_id>/status, commands/<device_id>/set

import network, time, machine, ubinascii, json, dht, utime
from umqtt.simple import MQTTClient
from machine import Pin, ADC, I2C, PWM
# urequests for backend sync (optional for later)

### ========== CONFIG ========== ###
DEVICE_ID = "esp32_chili_01"

# WiFi
WIFI_SSID = "hotspotkeren"
WIFI_PASS = "87654321"

# MQTT
MQTT_BROKER = "192.168.137.1"   # hotspot IP (accessible from other devices on same hotspot)
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASS = None

TOPIC_SENSORS = b"esp32/chili/data"        # Must match backend config!
TOPIC_ACTUATORS = b"esp32/chili/status"
TOPIC_COMMANDS = b"esp32/chili/cmd"        # Must match backend config!

# Pins (sesuaikan)
PIN_DHT = 15
PIN_PH_ADC = 35        # pH sensor
PIN_SOIL_ADC = 34      # Soil moisture sensor
PIN_LIFT_LEFT = 26     # Relay lift kiri
PIN_LIFT_RIGHT = 25    # Relay lift kanan
PIN_SERVO_LEFT = 27    # Servo lid kiri (PWM)
PIN_SERVO_RIGHT = 14   # Servo lid kanan (PWM)
PIN_WATER_PUMP = 13    # Relay water pump

# BH1750 usage toggle
USE_BH1750 = True

# Soil thresholds (percentage)
SOIL_DRY_THRESHOLD = 40      # if soil_moisture < 40% => dry, need watering
SOIL_WET_THRESHOLD = 70      # if soil_moisture > 70% => wet, stop watering

# Lift safety (untuk lifting mechanism)
LIFT_MAX_RUNTIME_SEC = 30  # max seconds lift can run continuously
LIFT_MIN_OFF_SEC = 5       # minimum off time between runs

# Pump safety (untuk water pump)
PUMP_MAX_RUNTIME_SEC = 60  # max seconds pump can run continuously
PUMP_MIN_OFF_SEC = 10      # minimum off time between pump runs

# Servo positions untuk lid control
SERVO_LID_OPEN = 90    # Servo angle untuk buka lid (tarik tali)
SERVO_LID_CLOSE = 0    # Servo angle untuk tutup lid (longgarkan tali)

# Sensor read/publish intervals
READ_INTERVAL = 20  # seconds

### ========== END CONFIG ========== ###


# --- utility: wifi connect ---
def connect_wifi(ssid, pwd):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.active(True)
        wlan.connect(ssid, pwd)
        t0 = time.time()
        while not wlan.isconnected():
            time.sleep(0.5)
            if time.time() - t0 > 15:
                print("WiFi connect timeout")
                break
    print("WiFi status:", wlan.ifconfig())
    return wlan.isconnected()

# --- BH1750 driver (simple, for 1 lx resolution mode) ---
class BH1750:
    PWR_DOWN = 0x00
    PWR_ON = 0x01
    RESET = 0x07
    CONT_HIGH_RES = 0x10
    CONT_LOW_RES = 0x13
    ONE_TIME_HIGH_RES = 0x20

    def __init__(self, i2c, addr=0x23):
        self.i2c = i2c
        self.addr = addr

    def read(self):
        try:
            self.i2c.writeto(self.addr, bytes([self.CONT_HIGH_RES]))
            time.sleep(0.18)
            data = self.i2c.readfrom(self.addr, 2)
            raw = (data[0] << 8) | data[1]
            lux = raw / 1.2
            return lux
        except Exception as e:
            print("BH1750 read error:", e)
            return None

# --- pH mapping (simple linear mapping) ---
PH_ADC_MIN = 0     
PH_ADC_MAX = 4095  
PH_PH_MIN = 0.0
PH_PH_MAX = 14.0

def adc_to_ph(adc_value):
    v = max(0, min(4095, adc_value))
    ph = PH_PH_MIN + (v - PH_ADC_MIN) * (PH_PH_MAX - PH_PH_MIN) / (PH_ADC_MAX - PH_ADC_MIN)
    return round(ph, 2)

# --- setup hardware ---
dht_sensor = dht.DHT22(Pin(PIN_DHT))
soil_adc = ADC(Pin(PIN_SOIL_ADC)); soil_adc.atten(ADC.ATTN_11DB); soil_adc.width(ADC.WIDTH_12BIT)
ph_adc = ADC(Pin(PIN_PH_ADC)); ph_adc.atten(ADC.ATTN_11DB); ph_adc.width(ADC.WIDTH_12BIT)

# Lift relays (both normally OFF)
lift_left = Pin(PIN_LIFT_LEFT, Pin.OUT)
lift_right = Pin(PIN_LIFT_RIGHT, Pin.OUT)
lift_left.value(0)
lift_right.value(0)

# Water pump relay (normally OFF)
water_pump = Pin(PIN_WATER_PUMP, Pin.OUT)
water_pump.value(0)

# Two servos for lid control (left & right) using PWM (50Hz)
servo_left = PWM(Pin(PIN_SERVO_LEFT), freq=50)
servo_right = PWM(Pin(PIN_SERVO_RIGHT), freq=50)

def servo_angle_to_duty(angle):
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    duty = int(25 + (angle / 180.0) * (128 - 25))
    return duty

def set_servo_left(angle):
    duty = servo_angle_to_duty(angle)
    servo_left.duty(duty)

def set_servo_right(angle):
    duty = servo_angle_to_duty(angle)
    servo_right.duty(duty)

def set_both_servos(angle):
    """Set both left and right servos to same angle"""
    set_servo_left(angle)
    set_servo_right(angle)

# I2C dan BH1750 (pin SDA=21, SCL=22)
i2c = None
bh1750 = None
if USE_BH1750:
    try:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
        bh1750 = BH1750(i2c)
    except Exception as e:
        print("I2C init error:", e)
        bh1750 = None

# MQTT client
client = None

def mqtt_connect():
    global client
    client_id = ubinascii.hexlify(machine.unique_id())
    client = MQTTClient(client_id, MQTT_BROKER, MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)
    client.set_callback(on_mqtt_message)
    try:
        client.connect()
        client.subscribe(TOPIC_COMMANDS)
        print("Connected to MQTT broker, subscribed to", TOPIC_COMMANDS)
        return True
    except Exception as e:
        print("MQTT connect fail:", e)
        return False

AUTO_MODE = True
lift_running_since = 0
last_lift_stop = 0
pump_running_since = 0
last_pump_stop = 0
lid_state = "CLOSED"  # OPEN or CLOSED

def lift_up():
    """Raise both lift relays"""
    global lift_running_since
    lift_left.value(1)
    lift_right.value(1)
    lift_running_since = time.time()
    print("[LIFT] Both relays UP")
    publish_actuator({"lift": "UP", "relay_left": PIN_LIFT_LEFT, "relay_right": PIN_LIFT_RIGHT, "ts": ts_now_str()})

def lift_down():
    """Lower both lift relays"""
    global lift_running_since, last_lift_stop
    lift_left.value(0)
    lift_right.value(0)
    lift_running_since = 0
    last_lift_stop = time.time()
    print("[LIFT] Both relays DOWN")
    publish_actuator({"lift": "DOWN", "relay_left": PIN_LIFT_LEFT, "relay_right": PIN_LIFT_RIGHT, "ts": ts_now_str()})

def pump_on():
    """Turn on water pump"""
    global pump_running_since
    water_pump.value(1)
    pump_running_since = time.time()
    print("[PUMP] Water pump ON")
    publish_actuator({"pump": "ON", "relay_pin": PIN_WATER_PUMP, "ts": ts_now_str()})

def pump_off():
    """Turn off water pump"""
    global pump_running_since, last_pump_stop
    water_pump.value(0)
    pump_running_since = 0
    last_pump_stop = time.time()
    print("[PUMP] Water pump OFF")
    publish_actuator({"pump": "OFF", "relay_pin": PIN_WATER_PUMP, "ts": ts_now_str()})

def open_lid():
    """Open box lid (both servos pull rope)"""
    global lid_state
    set_both_servos(SERVO_LID_OPEN)
    lid_state = "OPEN"
    print("[LID] Opening... servo angle =", SERVO_LID_OPEN)
    publish_actuator({"lid": "OPEN", "servo_left": SERVO_LID_OPEN, "servo_right": SERVO_LID_OPEN, "ts": ts_now_str()})

def close_lid():
    """Close box lid (both servos release rope)"""
    global lid_state
    set_both_servos(SERVO_LID_CLOSE)
    lid_state = "CLOSED"
    print("[LID] Closing... servo angle =", SERVO_LID_CLOSE)
    publish_actuator({"lid": "CLOSED", "servo_left": SERVO_LID_CLOSE, "servo_right": SERVO_LID_CLOSE, "ts": ts_now_str()})

def on_mqtt_message(topic, msg):
    global AUTO_MODE
    try:
        payload = json.loads(msg)
    except:
        print("Invalid MQTT payload:", msg)
        return
    print("[MQTT-CMD]", payload)
    
    # Lift control (both relays)
    if "lift" in payload:
        cmd = payload["lift"].lower()
        if cmd == "up":
            AUTO_MODE = False
            lift_up()
        elif cmd == "down":
            AUTO_MODE = False
            lift_down()
    
    # Lid control (servo-based)
    if "lid" in payload:
        cmd = payload["lid"].lower()
        if cmd == "open":
            open_lid()
        elif cmd == "close":
            close_lid()
    
    # Water pump control
    if "pump" in payload:
        cmd = payload["pump"].lower()
        if cmd == "on":
            pump_on()
        elif cmd == "off":
            pump_off()
    
    # Direct servo angle control
    if "servo" in payload:
        try:
            angle = int(payload["servo"])
            set_both_servos(angle)
            publish_actuator({"servo_left": angle, "servo_right": angle, "ts": ts_now_str()})
        except:
            print("Invalid servo angle")
    
    # Auto mode toggle
    if "auto" in payload:
        if payload["auto"] in [True, False]:
            AUTO_MODE = payload["auto"]
            publish_actuator({"auto_mode": AUTO_MODE, "ts": ts_now_str()})

def ts_now_str():
    t = utime.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[0:6])

def publish_sensors(payload):
    try:
        client.publish(TOPIC_SENSORS, json.dumps(payload))
    except Exception as e:
        print("Publish sensors fail:", e)

def publish_actuator(payload):
    try:
        client.publish(TOPIC_ACTUATORS, json.dumps(payload))
    except Exception as e:
        print("Publish actuators fail:", e)

def read_all_sensors():
    data = {"device_id": DEVICE_ID, "ts": ts_now_str()}
    try:
        dht_sensor.measure()
        data["temperature_c"] = round(dht_sensor.temperature(), 2)
        data["humidity_pct"] = round(dht_sensor.humidity(), 2)
    except Exception as e:
        print("DHT read err:", e)
        data["temperature_c"] = None
        data["humidity_pct"] = None

    if bh1750:
        lux = bh1750.read()
        data["lux"] = round(lux,2) if lux is not None else None

    try:
        soil_val = soil_adc.read()
        # Convert raw ADC (0-4095) to percentage (0-100%)
        soil_percent = max(0, min(100, int((soil_val / 4095) * 100)))
        data["soil_moisture"] = soil_percent
    except:
        data["soil_moisture"] = None

    try:
        ph_val = ph_adc.read()
        data["ph"] = adc_to_ph(ph_val)
    except:
        data["ph"] = None

    # Add light sensor data if available
    if bh1750:
        lux = bh1750.read()
        data["light_lux"] = round(lux, 2) if lux is not None else None

    return data

def automation_check_and_act(data):
    """Check soil moisture and automatically control pump and lift mechanism"""
    global lift_running_since, last_lift_stop, pump_running_since, last_pump_stop
    if data["soil_moisture"] is None:
        return
    soil = data["soil_moisture"]
    now = time.time()
    is_dry = soil < SOIL_DRY_THRESHOLD       # Lower percentage = drier soil
    is_wet = soil > SOIL_WET_THRESHOLD       # Higher percentage = wetter soil

    # Safety: max runtime for lift
    if lift_running_since:
        if now - lift_running_since > LIFT_MAX_RUNTIME_SEC:
            print("[AUTO] Lift max runtime exceeded — stopping")
            lift_down()
            return

    # Safety: max runtime for pump
    if pump_running_since:
        if now - pump_running_since > PUMP_MAX_RUNTIME_SEC:
            print("[AUTO] Pump max runtime exceeded — stopping")
            pump_off()
            return

    if AUTO_MODE:
        # Auto-control pump based on soil moisture
        if is_dry and not pump_running_since:
            # Soil is dry and pump is off → turn on
            min_off_time = now - last_pump_stop if last_pump_stop else float('inf')
            if min_off_time >= PUMP_MIN_OFF_SEC:
                print("[AUTO] Soil dry ({:.0f}%) — turning pump ON".format(soil))
                pump_on()
        
        elif is_wet and pump_running_since:
            # Soil is wet and pump is on → turn off
            print("[AUTO] Soil wet ({:.0f}%) — turning pump OFF".format(soil))
            pump_off()

def main_loop():
    if not connect_wifi(WIFI_SSID, WIFI_PASS):
        print("Warning: WiFi not connected — continuing but MQTT will fail.")
    if not mqtt_connect():
        print("MQTT connect failed — will retry in loop.")

    last_read = 0
    while True:
        try:
            try:
                client.check_msg()
            except Exception as e:
                print("MQTT check_msg error:", e)
                time.sleep(1)
                try:
                    mqtt_connect()
                except:
                    pass

            now = time.time()
            if now - last_read >= READ_INTERVAL:
                last_read = now
                sensor_payload = read_all_sensors()
                print("Sensors:", sensor_payload)
                publish_sensors(sensor_payload)
                automation_check_and_act(sensor_payload)

            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped by user")
            break
        except Exception as e:
            print("Main loop exception:", e)
            time.sleep(2)

if __name__ == "__main__":
    main_loop()
