import paho.mqtt.client as mqtt
import time
import random
import json
import uuid

# Generate a unique ID for this device
id = str(uuid.uuid4())  # Using UUID for guaranteed uniqueness
client_name = id + '_temperature_client'

# Define MQTT topics
telemetry_topic = f'{id}/telemetry'
command_topic = f'{id}/commands'

# Create MQTT client and connect to broker
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT connected! Client name: {client_name}")
print(f"Device ID: {id}")
print(f"Telemetry topic: {telemetry_topic}")
print(f"Command topic: {command_topic}")

def simulate_temperature():
    """Simulate temperature readings between 20-30°C"""
    return random.uniform(20, 30)

def on_publish(client, userdata, mid):
    """Callback function that is called when a message is successfully published"""
    print(f"Message {mid} published successfully")

def handle_command(client, userdata, message):
    """Handle incoming command messages"""
    try:
        command = json.loads(message.payload.decode())
        print(f"Command received: {command}")
        
        # Process the LED command
        led_on = command.get('led_on', False)
        print(f"LED state: {'ON' if led_on else 'OFF'}")
        
    except json.JSONDecodeError:
        print("Error: Received invalid JSON command")
    except Exception as e:
        print(f"Error processing command: {e}")

def main():
    try:
        # Set up the publish callback
        mqtt_client.on_publish = on_publish
        
        # Subscribe to command topic
        mqtt_client.subscribe(command_topic)
        mqtt_client.on_message = handle_command
        
        while True:
            # Simulate temperature reading
            temperature = simulate_temperature()
            
            # Create telemetry data
            telemetry = {
                'temperature': temperature,
                'timestamp': time.time(),
                'device_id': id
            }
            
            # Convert to JSON and publish
            message = json.dumps(telemetry)
            result = mqtt_client.publish(telemetry_topic, message)
            
            # Wait for the message to be published
            result.wait_for_publish()
            
            print(f"Published temperature: {temperature:.1f}°C")
            
            # Wait for 3 seconds before next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except Exception as e:
        print(f"An error occurred: {e}")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main() 