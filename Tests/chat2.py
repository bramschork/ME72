#!/usr/bin/env python3
import serial
import struct
import time


def crc16(data: bytes) -> int:
    """
    Calculate the 16-bit CRC (polynomial 0x1021) used by RoboClaw.
    """
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # ensure CRC remains 16-bit
    return crc


def get_version(ser: serial.Serial, address: int = 0x80) -> str:
    """
    Sends the GETVERSION command (code 21) to the RoboClaw and returns the firmware version string.
    """
    command = 21  # GETVERSION command code
    # Build the packet: [address, command] + CRC
    packet = bytes([address, command])
    crc = crc16(packet)
    packet += struct.pack('>H', crc)  # Append CRC as 2 bytes (big-endian)

    ser.write(packet)
    # Wait briefly for the RoboClaw to respond
    time.sleep(0.1)
    response = ser.read(64)

    return response.decode('ascii', errors='ignore')


def read_eeprom(ser: serial.Serial, address: int, location: int) -> int:
    """
    Reads one byte from the EEPROM at the given location.

    The EEPROM read command is 0xA0. The packet structure is:
      [address, 0xA0, location] + CRC
    """
    command = 0xA0  # EEPROM read command code
    packet = bytes([address, command, location])
    crc = crc16(packet)
    packet += struct.pack('>H', crc)

    ser.write(packet)
    # A brief delay to allow the RoboClaw to process the command
    time.sleep(0.05)

    response = ser.read(1)
    if len(response) < 1:
        print(f"Error: No response for EEPROM location {location}")
        return None
    return response[0]


def eeprom_dump(ser: serial.Serial, address: int = 0x80, num_bytes: int = 64):
    """
    Dumps the first `num_bytes` of EEPROM.

    This function iterates through EEPROM addresses 0 to num_bytes-1 and prints
    each byte (in hex format). These bytes often include settings like baud rate,
    acceleration, timeout, etc.
    """
    print("EEPROM Dump:")
    for i in range(num_bytes):
        value = read_eeprom(ser, address, i)
        if value is not None:
            print(f"Addr 0x{i:02X}: 0x{value:02X}")
        else:
            print(f"Addr 0x{i:02X}: Read Error")


def main():
    # Configure these settings for your environment
    # Change as needed (e.g., /dev/ttyAMA0 or /dev/serial0)
    port = "/dev/ttyS0"
    baudrate = 38400     # Must match your RoboClaw's configured baud rate
    address = 0x80       # Default RoboClaw address; update if necessary

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # Get and print the firmware version.
    version = get_version(ser, address)
    print("Firmware version:", version.strip())

    # Dump EEPROM contents.
    eeprom_dump(ser, address, num_bytes=64)

    ser.close()


if __name__ == "__main__":
    main()
