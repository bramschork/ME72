import serial

# Open the serial port
ser = serial.Serial('/dev/serial0', 38400)  # Adjust baud rate as needed

# Send a test command (replace with a valid RoboClaw command)
ser.write(b'\xAA\x80\x00\x00')

# Optionally, read response
response = ser.read(10)  # Adjust byte count if needed
print(response)

# Close the serial port
ser.close()
