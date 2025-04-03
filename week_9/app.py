import json
import time
import paho.mqtt.client as mqtt

# Use the same ID as in mqtt_temp.py
id = 'test_device_001'
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'
client_name = id + '_temperature_server'

# Create MQTT client
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"Server started! Listening for messages from {client_telemetry_topic}")

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print(f"Temperature received: {payload['temperature']:.1f}°C")
        
        # Send command based on temperature
        command = {'led_on': payload['temperature'] > 25}
        print(f"Sending command: {command}")
        client.publish(server_command_topic, json.dumps(command))
        
    except Exception as e:
        print(f"Error handling telemetry: {e}")

# Subscribe to telemetry topic
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

def main():
    try:
        while True:
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except Exception as e:
        print(f"An error occurred: {e}")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main() 