import json
import threading
import time
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, topic, on_message_cb=None):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_message_cb = on_message_cb
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._thread = None

    def _on_connect(self, client, userdata, flags, rc):
        print('Connected to MQTT broker with result code', rc)
        client.subscribe(self.topic)

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
        except Exception:
            data = msg.payload.decode('utf-8')
        if self.on_message_cb:
            self.on_message_cb(msg.topic, data)

    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        # run network loop in background thread
        self._thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self._thread.start()

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            # loop_forever runs until disconnect; give it a moment
            time.sleep(0.1)
