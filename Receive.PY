import serial
import requests
import time

THINGSPEAK_API_KEY = "R6R5UOCQZC0B61YL"
THINGSPEAK_CHANNEL_ID = "2719266"
SERIAL_PORT = "COM9"   
BAUD_RATE = 9600

# Connect to Arduino

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  
  
def get_sensor_data():
    """Fetch sensor data from ThingSpeak."""
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?results=1&api_key={THINGSPEAK_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        last_entry = data["feeds"][-1]
        return {
            "rain": int(last_entry.get("field4", 0)),  # Default to 0 if None
            "moisture": int(last_entry.get("field3", 0)),
            "ldr": int(last_entry.get("field5", 0))
        }
    else:
        print("Failed to fetch data from ThingSpeak.")
        return None

def format_commands(data):
    """Format commands into a single string for Arduino."""
    commands = []
    if data["rain"] > 30:
        commands.append("BUZZER_ON")
    else:
        commands.append("BUZZER_OFF")
    
    if data["moisture"] < 30:
        commands.append("SERVO_RUN")
    
    if data["ldr"] > 50:
        commands.append("LED_GREEN")
    else:
        commands.append("LED_RED") 
    
    # moisture value
    commands.append(f"MOISTURE:{data['moisture']}")
    
    return ",".join(commands) + "\n"  # Combine commands, separated by commas

def main():
    while True:
        sensor_data = get_sensor_data()
        if sensor_data:
            print(f"Sensor Data: {sensor_data}")
            command_string = format_commands(sensor_data)
            print(f"Sending to Arduino: {command_string.strip()}")
            arduino.write(command_string.encode())  # Send formatted commands
        time.sleep(15)  # Fetch data every 15 seconds

if __name__ == "__main__":
    main()
