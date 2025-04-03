import json
import time
import paho.mqtt.client as mqtt
import uuid

id = str(uuid.uuid4())
client_name = id + '_temperature_server'

telemetry_topic = f'{id}/telemetry'
command_topic = f'{id}/commands'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT Server connected! Client name: {client_name}")
print(f"Server ID: {id}")
print(f"Listening to topic: {telemetry_topic}")
print(f"Sending commands to topic: {command_topic}")

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print(f"Message received: {payload}")
        
        temperature = payload.get('temperature')
        if temperature is not None:
            print(f"Temperature: {temperature:.1f}°C")
            
            command = {
                'led_on': temperature > 25
            }
            command_message = json.dumps(command)
            result = mqtt_client.publish(command_topic, command_message)
            result.wait_for_publish()
            print(f"Sent command: {command}")
            
    except json.JSONDecodeError:
        print("Error: Received invalid JSON data")
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    try:
        mqtt_client.subscribe(telemetry_topic)
        mqtt_client.on_message = handle_telemetry
        
        print("Server is running. Press Ctrl+C to exit.")
        
        while True:
            time.sleep(1)
            
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