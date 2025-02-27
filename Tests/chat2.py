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
    """
    command = 21  # GETVERSION command code
    packet = bytes([address, command])
    crc = crc16(packet)
    packet += struct.pack('>H', crc)

    # Flush any leftover input before sending a new command.
    ser.reset_input_buffer()

    ser.write(packet)
    time.sleep(0.1)

    response = ser.read(64)
    return response.decode('ascii', errors='ignore')


def read_eeprom_settings(ser: serial.Serial, address: int = 0x80) -> tuple:
    """
    Sends the Read Settings from EEPROM command (command code 95) to the RoboClaw and returns the settings.

    According to the documentation:
      Send: [Address, 95]
      Receive: [Enc1Mode, Enc2Mode, CRC(2 bytes)]

    Raises:
      Exception if the response is incomplete or the CRC check fails.
    """
    command = 95  # EEPROM settings command
    # Flush input buffer to remove any previous data.
    ser.reset_input_buffer()

    packet = bytes([address, command])
    ser.write(packet)
    # Increase delay in case the response is slower.
    time.sleep(0.2)

    response = ser.read(4)
    if len(response) != 4:
        # For debugging: print out any data that was received.
        print(f"Debug: Received raw data: {response}")
        raise Exception("Incomplete response from EEPROM settings command.")

    enc1_mode, enc2_mode = response[0], response[1]
    received_crc = struct.unpack('>H', response[2:])[0]
    calculated_crc = crc16(response[:2])

    if received_crc != calculated_crc:
        raise Exception(
            f"CRC mismatch: received {received_crc:04X}, calculated {calculated_crc:04X}")

    return enc1_mode, enc2_mode


def main():
    # Adjust if necessary (e.g., /dev/ttyAMA0 or /dev/serial0)
    port = "/dev/ttyS0"
    baudrate = 38400    # Must match your RoboClaw settings

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
