import time
from roboclaw_3 import Roboclaw

# Serial Configuration
serial_port = "/dev/serial0"  # Use /dev/serial0 for Raspberry Pi
baudrate = 38400              # Match this with the new baud rate
address = 0x80                # Default RoboClaw address

# Initialize RoboClaw Object
roboclaw = Roboclaw(serial_port, baudrate)

# Open Serial Connection
if roboclaw.Open():
    print("Connected to RoboClaw.")
else:
    print("Failed to connect to RoboClaw.")
    exit()


def set_baud_rate_38400():
    print("Setting Baud Rate to 38400...")

    # Baud Rate Code for 38400 is 0x04
    baud_rate_code = 0x04

    # Set Configuration Command
    # 0x62 is SETCONFIG command
    success = roboclaw._write2(
        address, roboclaw.Cmd.SETCONFIG, baud_rate_code)

    if success:
        print("Baud rate set to 38400. Saving to EEPROM...")
        # Save the new baud rate to EEPROM to make it permanent
        roboclaw.WriteNVM(address)
        print("Baud rate saved to EEPROM.")
    else:
        print("Failed to set baud rate.")


if __name__ == "__main__":
    set_baud_rate_38400()
    roboclaw._port.close()
