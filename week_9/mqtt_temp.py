import paho.mqtt.client as mqtt
import time
import random
import json

id = 'test_device_001'  
client_name = id + '_temperature_client'


mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT connected! Client name: {client_name}")

def simulate_temperature():
    return random.uniform(20, 30)

def main():
    try:
        while True:
         
            temperature = simulate_temperature()
            
        
            led_state = temperature > 25
            print(f"Temperature: {temperature:.1f}°C, LED: {'ON' if led_state else 'OFF'}")
            
      
            telemetry = {
                'temperature': temperature,
                'led_state': led_state
            }
            mqtt_client.publish(f'{id}/telemetry', json.dumps(telemetry))
            
         
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