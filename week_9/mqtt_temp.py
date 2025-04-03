import paho.mqtt.client as mqtt
import time
import json
import os
import glob
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
LED_PIN = 17  
GPIO.setup(LED_PIN, GPIO.OUT)

# DS18B20 setup
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    try:
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    except Exception as e:
        print(f"Error reading temperature sensor: {e}")
        return None

def read_temp():
    try:
        lines = read_temp_raw()
        if lines is None:
            return None
            
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
            
        temp_pos = lines[1].find('t=')
        if temp_pos != -1:
            temp_string = lines[1][temp_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
    except Exception as e:
        print(f"Error processing temperature data: {e}")
        return None

# MQTT setup
id = 'test_device_001'  # Replace with your unique ID
client_name = id + '_temperature_client'
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

print(f"MQTT connected! Client name: {client_name}")

def handle_command(client, userdata, message):
    try:
        command = json.loads(message.payload.decode())
        if 'led_on' in command:
            GPIO.output(LED_PIN, GPIO.HIGH if command['led_on'] else GPIO.LOW)
            print(f"LED turned {'ON' if command['led_on'] else 'OFF'}")
    except Exception as e:
        print(f"Error handling command: {e}")

mqtt_client.subscribe(server_command_topic)
mqtt_client.on_message = handle_command

def main():
    try:
        while True:
            # Read temperature
            temperature = read_temp()
            
            if temperature is not None:
                # Control LED based on temperature
                led_state = temperature > 25
                GPIO.output(LED_PIN, GPIO.HIGH if led_state else GPIO.LOW)
                
                print(f"Temperature: {temperature:.1f}°C, LED: {'ON' if led_state else 'OFF'}")
                
                # Send telemetry
                telemetry = {
                    'temperature': temperature,
                    'led_state': led_state
                }
                mqtt_client.publish(client_telemetry_topic, json.dumps(telemetry))
            else:
                print("Failed to read temperature")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        GPIO.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        GPIO.cleanup()

if __name__ == "__main__":
    main() 