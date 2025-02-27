import time
from roboclaw import Roboclaw

# Windows COM port example: "COM3"
# Linux tty port example: "/dev/ttyACM0"
# Replace with your actual port
port = "/dev/ttyACM0"
baud_rate = 115200

# Create RoboClaw object
roboclaw = Roboclaw(port, baud_rate)

# Open serial port
roboclaw.Open()

# RoboClaw device address
address = 0x80  # Default address; change if different


def read_eeprom_settings():
    print("Reading EEPROM settings...")
    for i in range(255):  # EEPROM addresses range from 0 to 254
        try:
            value = roboclaw.ReadEeprom(address, i)
            if value[0]:  # If read is successful
                print(f"EEPROM Address {i}: {value[1]}")
            else:
                print(f"Failed to read EEPROM address {i}")
        except Exception as e:
            print(f"Error reading EEPROM address {i}: {e}")


if __name__ == "__main__":
    read_eeprom_settings()
    roboclaw.Close()
