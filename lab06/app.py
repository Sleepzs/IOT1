import json
import time
import paho.mqtt.client as mqtt

class TemperatureMonitorServer:
    """Server application to receive telemetry and send commands"""
    
    def __init__(self, client_id, broker='test.mosquitto.org'):
        # Configure MQTT topics and client
        self.id = client_id
        self.telemetry_topic = f"{self.id}/telemetry"
        self.command_topic = f"{self.id}/commands"
        self.client_name = f"{self.id}_temperature_server"
        
        # Set temperature threshold for LED control
        self.temp_threshold = 25
        
        # Create and configure MQTT client
        self.client = mqtt.Client(client_id=self.client_name, protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.connect(broker)
        self.client.loop_start()
        print(f"MQTT server connected to {broker}!")
        
        # Set up message handler and debug info
        print(f"Subscribing to topic: {self.telemetry_topic}")
        self.client.subscribe(self.telemetry_topic)
        self.client.on_message = self._handle_telemetry
    
    def _handle_telemetry(self, client, userdata, message):
        """Process incoming temperature telemetry and send commands"""
        try:
            # Parse telemetry data
            payload = json.loads(message.payload.decode())
            print(f"Telemetry received: {payload}")
            
            # Determine if LED should be on based on temperature threshold
            temperature = payload.get('temperature')
            if temperature is None:
                print("Warning: Temperature value missing in telemetry")
                return
                
            command = {'led_on': temperature > self.temp_threshold}
            
            # Send command to control the LED
            self.client.publish(self.command_topic, json.dumps(command))
            print(f"Command sent: {command} (LED {'ON' if command['led_on'] else 'OFF'})")
            
        except json.JSONDecodeError:
            print(f"Error: Invalid telemetry format - {message.payload.decode()}")
        except Exception as e:
            print(f"Telemetry handling error: {e}")
    
    def run(self):
        """Run the server continuously"""
        try:
            print(f"Temperature monitor server running. LED threshold: {self.temp_threshold}°C")
            print("Press Ctrl+C to exit")
            
            # Keep the process alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nServer terminated by user")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up MQTT resources"""
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT connection closed")

def main():
    """Application entry point"""
    server = TemperatureMonitorServer('willasp')
    server.run()

if __name__ == "__main__":
    main() 