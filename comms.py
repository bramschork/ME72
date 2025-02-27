import time
from roboclaw_3 import Roboclaw

# Serial Configuration
serial_port = "/dev/ttyS0"  # Adjust to your serial port
baud_rate = 38400             # Match this with the RoboClaw baud rate
address = 0x80                # Default RoboClaw address

# Initialize RoboClaw Object
roboclaw = Roboclaw(serial_port, baud_rate)

# Open Serial Connection
roboclaw.Open()


def read_eeprom_settings():
    print("Reading EEPROM settings...")
    for i in range(255):  # EEPROM addresses range from 0 to 254
        try:
            # Read EEPROM address
            value = roboclaw.ReadEeprom(address, i)

            # Check if read was successful
            if value[0]:
                # Decode bytes to hex format to handle non-ASCII characters
                byte_value = value[1].to_bytes(1, 'big')
                print(f"EEPROM Address {i}: {byte_value.hex().upper()}")
            else:
                print(f"Failed to read EEPROM address {i}")
        except Exception as e:
            print(f"Error reading EEPROM address {i}: {e}")


if __name__ == "__main__":
    read_eeprom_settings()
    roboclaw.Close()
