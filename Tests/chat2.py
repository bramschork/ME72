#!/usr/bin/env python3
import serial
import struct
import time


def crc16(data: bytes) -> int:
    """
    Calculate the CRC-16 used by RoboClaw.
    Uses the polynomial 0x1021.
    """
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # ensure crc remains 16-bit
    return crc


def get_version(ser: serial.Serial, address: int = 0x80, command: int = 21) -> str:
    """
    Sends the GETVERSION command (command code 21) to the RoboClaw and returns the firmware version string.

    Parameters:
      ser      - an open serial.Serial instance
      address  - the RoboClaw address (default is 0x80; adjust if necessary)

    Returns:
      A string containing the firmware version info.
    """
    # command = 21  # GETVERSION command code (0x15 in hex)
    # Construct the packet: [address, command] followed by a 16-bit CRC.
    packet = bytes([address, command])
    crc = crc16(packet)
    packet += struct.pack('>H', crc)  # pack as big-endian unsigned short

    # Write the packet to the serial port
    ser.write(packet)
    # Give the RoboClaw a moment to process and reply
    time.sleep(0.1)

    # Read the response.
    # The response length can vary; here we read up to 64 bytes.
    response = ser.read(64)

    # Return decoded text, ignoring non-ASCII bytes if needed.
    return response.decode('ascii', errors='ignore')


def main():
    # Set the correct serial port and baud rate for your Raspberry Pi and RoboClaw.
    port = "/dev/ttyS0"  # e.g., /dev/ttyAMA0 or /dev/serial0 might be used instead
    baudrate = 38400    # adjust baud rate to match your RoboClaw settings

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    version = get_version(ser, command=21)
    print("Firmware version:", version.strip())

    version = get_version(ser, command=24)
    print("Battery version:", version.strip())

    version = get_version(ser, command=94)
    print("EEPROM:", version.strip())

    ser.close()

    ser.close()


if __name__ == "__main__":
    main()
