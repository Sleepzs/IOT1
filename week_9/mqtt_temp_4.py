import paho.mqtt.client as mqtt
import time
import json
import uuid
import RPi.GPIO as GPIO
import os
import glob


LED_PIN = 17 
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

id = str(uuid.uuid4()) 
client_name = id + '_temperature_client'

telemetry_topic = f'{id}/telemetry'
command_topic = f'{id}/commands'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT connected! Client name: {client_name}")
print(f"Device ID: {id}")
print(f"Telemetry topic: {telemetry_topic}")
print(f"Command topic: {command_topic}")

def read_temp_raw():
    try:
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def read_temperature():
    lines = read_temp_raw()
    if lines:
        try:
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
        except Exception as e:
            print(f"Error processing temperature: {e}")
    return None

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

def handle_command(client, userdata, message):
    try:
        command = json.loads(message.payload.decode())
        print(f"Command received: {command}")
        
        led_on = command.get('led_on', False)
        print(f"LED state: {'ON' if led_on else 'OFF'}")
        
        GPIO.output(LED_PIN, GPIO.HIGH if led_on else GPIO.LOW)
        
    except json.JSONDecodeError:
        print("Error: Received invalid JSON command")
    except Exception as e:
        print(f"Error processing command: {e}")

def cleanup():
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()

def main():
    try:
        mqtt_client.on_publish = on_publish
        
        mqtt_client.subscribe(command_topic)
        mqtt_client.on_message = handle_command
        
        GPIO.output(LED_PIN, GPIO.LOW)
        
        while True:
            temperature = read_temperature()
            
            if temperature is not None:
                telemetry = {
                    'temperature': temperature,
                    'timestamp': time.time(),
                    'device_id': id
                }
                
                message = json.dumps(telemetry)
                result = mqtt_client.publish(telemetry_topic, message)
                
                result.wait_for_publish()
                
                print(f"Published temperature: {temperature:.1f}°C")
            else:
                print("Failed to read temperature")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        cleanup()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main() 