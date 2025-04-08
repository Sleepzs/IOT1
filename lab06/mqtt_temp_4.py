import time
import json
import paho.mqtt.client as mqtt
from gpiozero import LED, Device
from gpiozero.pins.mock import MockFactory
import os
import glob

# Set MockFactory for non-Raspberry Pi environments
Device.pin_factory = MockFactory() if os.name == 'nt' else None

class TemperatureSensor:
    """Temperature sensor class for DS18B20 sensor communication"""
    def __init__(self):
        # Load required kernel modules
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        
        # Find temperature sensor device
        base_dir = '/sys/bus/w1/devices/'
        try:
            device_folder = glob.glob(base_dir + '28*')[0]
            self.device_file = device_folder + '/w1_slave'
        except IndexError:
            print("Warning: DS18B20 sensor not found")
            self.device_file = None

    def _read_raw_data(self):
        """Read raw temperature data from sensor file"""
        try:
            with open(self.device_file, 'r') as f:
                return f.readlines()
        except (FileNotFoundError, TypeError):
            print("Error: Unable to access temperature sensor")
            return None

    def get_temperature(self):
        """Get temperature readings in Celsius and Fahrenheit"""
        # Return early if sensor not available
        if self.device_file is None:
            return None, None

        lines = self._read_raw_data()
        if lines is None:
            return None, None
            
        try:
            # Wait for valid reading
            retries = 0
            while lines[0].strip()[-3:] != 'YES' and retries < 5:
                time.sleep(0.2)
                lines = self._read_raw_data()
                retries += 1
                if lines is None:
                    return None, None

            # Extract temperature value
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return round(temp_c, 2), round(temp_f, 2)
            return None, None
            
        except (IndexError, ValueError) as e:
            print(f"Error processing temperature data: {str(e)}")
            return None, None

class MQTTController:
    """MQTT controller for handling communications"""
    def __init__(self, client_id, broker='test.mosquitto.org'):
        self.id = client_id
        self.client_name = f"{self.id}_temperature_client"
        self.telemetry_topic = f"{self.id}/telemetry"
        self.command_topic = f"{self.id}/commands"
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=self.client_name, protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.connect(broker)
        self.client.loop_start()
        print(f"MQTT connected to {broker}!")
        
        # Initialize LED
        self.led = LED(17)
        
        # Subscribe to commands
        self.client.subscribe(self.command_topic)
        self.client.on_message = self._handle_command
    
    def _handle_command(self, client, userdata, message):
        """Process incoming MQTT commands"""
        try:
            payload = json.loads(message.payload.decode())
            print(f"Command received: {payload}")
            
            # Control LED based on command
            if 'led_on' in payload:
                if payload['led_on']:
                    self.led.on()
                    print("LED activated")
                else:
                    self.led.off()
                    print("LED deactivated")
        except json.JSONDecodeError:
            print(f"Error: Invalid command format")
        except Exception as e:
            print(f"Command handling error: {e}")
    
    def send_telemetry(self, celsius, fahrenheit):
        """Send temperature telemetry to MQTT broker"""
        if celsius is None:
            return False
            
        telemetry = {
            'temperature': celsius,  # For backward compatibility
            'temperature_c': celsius,
            'temperature_f': fahrenheit,
            'timestamp': time.time()
        }
        
        self.client.publish(self.telemetry_topic, json.dumps(telemetry))
        print(f"Telemetry sent: {telemetry}")
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.led.close()
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT connection closed")

def main():
    """Main function to monitor temperature and communicate via MQTT"""
    # Initialize components
    sensor = TemperatureSensor()
    mqtt = MQTTController('willasp')
    
    try:
        print("Temperature monitoring started. Press Ctrl+C to exit.")
        while True:
            # Get temperature readings
            celsius, fahrenheit = sensor.get_temperature()
            
            # Send telemetry if reading successful
            if celsius is not None:
                mqtt.send_telemetry(celsius, fahrenheit)
            else:
                print("Temperature reading failed, retrying...")
            
            # Wait before next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        # Ensure proper cleanup
        mqtt.cleanup()

if __name__ == "__main__":
    main() 