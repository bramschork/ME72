#!/usr/bin/env python3
import serial
import struct
import time


def crc16(data: bytes) -> int:
    """
    Calculate the CRC-16 used by RoboClaw.
    Uses the polynomial 0x1021 with an initial value of 0.
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


def crc16_alt(data: bytes, init: int = 0xFFFF) -> int:
    """
    Alternative CRC-16 calculation using an initial value of 0xFFFF.
    Some commands (like battery voltage) might use this variant.
    """
    crc = init
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def get_version(ser: serial.Serial, address: int = 0x80) -> str:
    """
    Sends the GETVERSION command (command code 21) to the RoboClaw
    and returns the firmware version string.

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
    packet += struct.pack('>H', crc)

    ser.write(packet)
    time.sleep(0.1)

    response = ser.read(64)
    return response.decode('ascii', errors='ignore')


def read_battery_voltage(ser: serial.Serial, address: int = 0x80) -> float:
    """
    Reads the main battery voltage level connected to B+ and B-.

    According to the documentation:
      Send: [Address, 24]
      Receive: [Value (2 bytes), CRC (2 bytes)]

    The voltage is returned in tenths of a volt (e.g., 300 = 30.0V).  
    This function uses an alternative CRC calculation (with initial value 0xFFFF)
    to verify the returned data.
    """
    command = 24  # Battery voltage command code
    ser.reset_input_buffer()

    packet = bytes([address, command])
    ser.write(packet)
    time.sleep(0.1)

    response = ser.read(4)
    if len(response) != 4:
        raise Exception("Incomplete response from battery voltage command.")

    voltage_raw = struct.unpack('>H', response[:2])[0]
    received_crc = struct.unpack('>H', response[2:])[0]
    calculated_crc = crc16_alt(response[:2])
    if received_crc != calculated_crc:
        raise Exception(
            f"CRC mismatch in battery voltage: received {received_crc:04X}, calculated {calculated_crc:04X}")

    voltage = voltage_raw / 10.0
    return voltage


def read_status(ser: serial.Serial, address: int = 0x80) -> int:
    """
    Reads the current unit status from the RoboClaw.

    According to the documentation:
      Send: [Address, 90]
      Receive: [Status (1 byte), CRC (2 bytes)]

    This function sends the command, reads 3 bytes, verifies the CRC over the status byte,
    and returns the status as an integer.
    """
    command = 90  # Read Status command code
    ser.reset_input_buffer()

    packet = bytes([address, command])
    ser.write(packet)
    time.sleep(0.1)

    response = ser.read(3)
    if len(response) != 3:
        raise Exception("Incomplete response from read status command.")

    status = response[0]
    received_crc = struct.unpack('>H', response[1:])[0]
    calculated_crc = crc16(response[:1])
    if received_crc != calculated_crc:
        raise Exception(
            f"CRC mismatch in read status: received {received_crc:04X}, calculated {calculated_crc:04X}")

    return status


def main():
    # Adjust if necessary (e.g., /dev/ttyAMA0 or /dev/serial0)
    port = "/dev/ttyS0"
    baudrate = 38400     # Must match your RoboClaw settings

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
        voltage = read_battery_voltage(ser)
        print(f"Battery Voltage: {voltage:.1f} V")
    except Exception as e:
        print("Error reading battery voltage:", e)

    try:
        status = read_status(ser)
        print(f"Status: {status:02X}")
    except Exception as e:
        print("Error reading status:", e)

    ser.close()


if __name__ == "__main__":
    main()
