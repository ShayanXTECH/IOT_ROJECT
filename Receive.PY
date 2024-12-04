import serial  # For communicating with the Arduino via serial port
import requests  # For making HTTP requests to the ThingSpeak API
import time  # For adding delays

# Define the ThingSpeak API key and channel ID
THINGSPEAK_API_KEY = "R6R5UOCQZC0B61YL"  # Replace with your ThingSpeak API key
THINGSPEAK_CHANNEL_ID = "2719266"  # Replace with your ThingSpeak channel ID

# Define the serial port and baud rate for Arduino communication
SERIAL_PORT = "COM9"  # Replace with the appropriate COM port for your Arduino
BAUD_RATE = 9600  # Ensure this matches the baud rate configured on the Arduino

# Initialize the serial connection to the Arduino
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)  # Set timeout for the serial connection
time.sleep(2)  # Allow time for the connection to stabilize

# Function to retrieve the latest sensor data from ThingSpeak
def get_sensor_data():
    # Construct the API endpoint URL for retrieving the latest feed
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?results=1&api_key={THINGSPEAK_API_KEY}"
    
    # Send an HTTP GET request to the ThingSpeak API
    response = requests.get(url)
    
    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Extract the last entry from the feeds
        last_entry = data["feeds"][-1]
        
        # Return the sensor data as a dictionary
        return {
            "rain": int(last_entry.get("field4", 0)),  # Rain sensor data (field 4)
            "moisture": int(last_entry.get("field3", 0)),  # Soil moisture data (field 3)
            "ldr": int(last_entry.get("field5", 0))  # LDR (light intensity) data (field 5)
        }
    else:
        # Return None if the request failed
        return None

# Function to determine commands based on sensor data
def format_commands(data):
    # Initialize an empty list to store commands
    commands = []
    
    # Determine if the buzzer should be on or off based on rain sensor data
    if data["rain"] > 30:  # Threshold for rain detection
        commands.append("BUZZER_ON")
    else:
        commands.append("BUZZER_OFF")
    
    # Determine if the servo motor should be activated based on soil moisture
    if data["moisture"] < 50:  # Threshold for dry soil
        commands.append("SERVO_RUN")
    
    # Determine the LED color based on light intensity (LDR data)
    if data["ldr"] > 50:  # Threshold for high light intensity
        commands.append("LED_GREEN")
    else:
        commands.append("LED_RED")
    
    # Combine all commands into a single string separated by commas
    return ",".join(commands) + "\n"

# Main function to handle the overall process
def main():
    while True:
        # Get the latest sensor data from ThingSpeak
        sensor_data = get_sensor_data()
        
        # If data retrieval was successful, format and send commands to Arduino
        if sensor_data:
            command_string = format_commands(sensor_data)  # Create the command string
            arduino.write(command_string.encode())  # Send the commands to Arduino
        
        # Wait for 15 seconds before the next iteration
        time.sleep(15)

# Entry point of the script
if __name__ == "__main__":
    main()  # Run the main function
