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


def get_version(ser: serial.Serial, address: int = 0x80) -> str:
    """
    Sends the GETVERSION command (command code 21) to the RoboClaw and returns the firmware version string.

    Parameters:
      ser      - an open serial.Serial instance
      address  - the RoboClaw address (default is 0x80; adjust if necessary)

    Returns:
      A string containing the firmware version info.
    """
    command = 21  # GETVERSION command code
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


def read_eeprom_settings(ser: serial.Serial, address: int = 0x80) -> tuple:
    """
    Sends the Read Settings from EEPROM command (command code 95) to the RoboClaw and returns the settings.

    According to the documentation:
      Send: [Address, 95]
      Receive: [Enc1Mode, Enc2Mode, CRC(2 bytes)]

    The function reads four bytes from the RoboClaw, verifies the CRC of the first two bytes,
    and returns a tuple (Enc1Mode, Enc2Mode).

    Raises:
      Exception if the response is incomplete or the CRC check fails.
    """
    command = 95  # Read Settings from EEPROM command
    packet = bytes([address, command])
    ser.write(packet)
    time.sleep(0.1)

    response = ser.read(4)
    if len(response) != 4:
        raise Exception("Incomplete response from EEPROM settings command.")

    # Unpack the response: first two bytes are encoder modes, next two bytes are the CRC.
    enc1_mode, enc2_mode = response[0], response[1]
    received_crc = struct.unpack('>H', response[2:])[0]

    # Calculate the CRC over the two settings bytes.
    calculated_crc = crc16(response[:2])
    if received_crc != calculated_crc:
        raise Exception(
            f"CRC mismatch: received {received_crc:04X}, calculated {calculated_crc:04X}")

    return enc1_mode, enc2_mode


def main():
    # Set the correct serial port and baud rate for your Raspberry Pi and RoboClaw.
    port = "/dev/ttyS0"  # e.g., /dev/ttyAMA0 or /dev/serial0 might be used instead
    baudrate = 38400    # adjust baud rate to match your RoboClaw settings

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    try:
        version = get_version(ser)
        print("Firmware version:", version.strip())
    except Exception as e:
        print("Error getting version:", e)

    try:
        enc1_mode, enc2_mode = read_eeprom_settings(ser)
        print("EEPROM Settings:")
        print(f"  Encoder 1 Mode: {enc1_mode}")
        print(f"  Encoder 2 Mode: {enc2_mode}")
    except Exception as e:
        print("Error reading EEPROM settings:", e)

    ser.close()


if __name__ == "__main__":
    main()
