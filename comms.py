import serial
from time import sleep

# Serial Configuration
serial_port = "/dev/ttyS0"  # Use /dev/serial0 for Raspberry Pi
baudrate = 38400              # Match this with the RoboClaw baud rate
address = 0x80                # Default RoboClaw address

# Initialize Serial Connection
roboclaw = serial.Serial(serial_port, baudrate, timeout=1)


def read_settings_from_eeprom():
    print("Requesting Settings from EEPROM...")
    # Construct the packet for Read Settings from EEPROM
    packet = [address, 95]  # 95 = Read Settings from EEPROM Command
    checksum = address ^ 95
    packet.append(checksum)

    # Send the packet
    roboclaw.write(bytes(packet))
    sleep(0.1)  # Short delay for processing

    # Read the response (up to 32 bytes)
    response = roboclaw.read(32)

    if response:
        print("EEPROM Settings Response:", response.hex())
    else:
        print("No response from RoboClaw. Check wiring and baud rate.")


if __name__ == "__main__":
    print("Communicating with RoboClaw...")

    # Read and print settings from EEPROM
    read_settings_from_eeprom()

    # Close the serial connection
    roboclaw.close()
