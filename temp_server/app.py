import json
import time
import paho.mqtt.client as mqtt

# Unique ID for the device/server
id = '67e6ce98-537b-414e-871f-f0cbc009ee63'

# Topic to receive temperature data
client_telemetry_topic = id + '/telemetry'

# Topic to send commands (like turning the LED on/off)
server_command_topic = id + '/commands'

# Name for the MQTT client
client_name = id + 'temperature_server'

# Create MQTT client and connect to broker
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()  # Start listening for messages in the background

# Function to handle received telemetry messages
def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())  # Decode the JSON message
    print("Message received:", payload)

    # Send a command: turn LED on if temperature > 25
    command = {'led_on': payload['temperature'] > 25}
    print("Sending command:", command)
    client.publish(server_command_topic, json.dumps(command))  # Send command

# Subscribe to telemetry topic and set callback
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

# Print status messages
print(f"Server started! Listening for messages on topic: {client_telemetry_topic}")
print(f"Sending commands on topic: {server_command_topic}")

# Keep the server running until the user stops it
try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("\nServer stopped by user")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
