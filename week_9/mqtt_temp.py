import paho.mqtt.client as mqtt
import time
import random
import json

# Generate a unique ID for this device
id = 'test_device_001'  # You can replace this with a GUID from GUIDGen
client_name = id + '_temperature_client'

# Create MQTT client and connect to broker
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT connected! Client name: {client_name}")

def simulate_temperature():
    """Simulate temperature readings between 20-30°C"""
    return random.uniform(20, 30)

def main():
    try:
        while True:
            # Simulate temperature reading
            temperature = simulate_temperature()
            
            # Control LED based on temperature
            led_state = temperature > 25
            print(f"Temperature: {temperature:.1f}°C, LED: {'ON' if led_state else 'OFF'}")
            
            # Send telemetry data
            telemetry = {
                'temperature': temperature,
                'led_state': led_state
            }
            mqtt_client.publish(f'{id}/telemetry', json.dumps(telemetry))
            
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