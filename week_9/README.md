# MQTT Temperature Monitoring System

This project implements a temperature monitoring system using MQTT protocol. It simulates a temperature sensor and LED control system that can be later adapted for use with real hardware on a Raspberry Pi.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the temperature monitoring script:
```bash
python mqtt_temp.py
```

The script will:
- Connect to the MQTT broker (test.mosquitto.org)
- Simulate temperature readings every 3 seconds
- Print the current temperature and LED state
- Publish telemetry data to the MQTT broker

To stop the script, press Ctrl+C.

## Features

- Simulated temperature readings (20-30°C range)
- LED state control based on temperature threshold (>25°C)
- MQTT telemetry publishing
- Graceful error handling and shutdown 