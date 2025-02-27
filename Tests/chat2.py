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
            crc &= 0xFFFF  # keep crc 16-bit
    return crc


def get_version(ser: serial.Serial, address: int = 0x80) -> str:
    """
    Sends the GETVERSION command (command code 21) to the RoboClaw
    and returns the firmware version string.
    """
    command = 21  # GETVERSION command code
    packet = bytes([address, command])
    crc = crc16(packet)
    packet += struct.pack('>H', crc)  # Append 16-bit CRC (big-endian)

    ser.write(packet)
    # Allow time for the RoboClaw to process and reply
    time.sleep(0.1)
    response = ser.read(64)
    return response.decode('ascii', errors='ignore')


def send_duty(ser: serial.Serial, address: int, command: int, duty: int) -> None:
    """
    Sends a duty command to one of the motors.

    Parameters:
      ser      - an open serial.Serial instance
      address  - the RoboClaw address (default is 0x80)
      command  - command code (0 for motor 1 duty, 1 for motor 2 duty)
      duty     - a signed 32-bit integer representing duty cycle.
                 (Assuming full power is 10000, 20% power is 2000)
    """
    # Pack address, command, and 4-byte signed duty value (big-endian)
    packet = bytes([address, command]) + struct.pack('>i', duty)
    crc = crc16(packet)
    packet += struct.pack('>H', crc)
    ser.write(packet)


def cycle_motors(ser: serial.Serial, address: int = 0x80, duty_on: int = 2000, delay: float = 1.0):
    """
    Cycles both motors on and off.

    Motors are turned on at duty `duty_on` for `delay` seconds, then off (duty=0)
    for `delay` seconds. Runs indefinitely until a KeyboardInterrupt is received.
    """
    print("Cycling motors. Press Ctrl+C to stop.")
    try:
        while True:
            # Turn on both motors (command 0 for M1, 1 for M2)
            send_duty(ser, address, 0, duty_on)  # Motor 1 on
            send_duty(ser, address, 1, duty_on)  # Motor 2 on
            print("Motors ON")
            time.sleep(delay)
            # Turn off both motors
            send_duty(ser, address, 0, 0)  # Motor 1 off
            send_duty(ser, address, 1, 0)  # Motor 2 off
            print("Motors OFF")
            time.sleep(delay)
    except KeyboardInterrupt:
        # Ensure motors are stopped if the loop is interrupted
        send_duty(ser, address, 0, 0)
        send_duty(ser, address, 1, 0)
        print("\nMotor cycling interrupted. Motors stopped.")


def main():
    port = "/dev/ttyS0"   # Adjust as needed, e.g., /dev/ttyAMA0 or /dev/serial0
    baudrate = 38400      # Set the baud rate to match your RoboClaw configuration
    address = 0x80        # RoboClaw default address; change if necessary

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # Retrieve and display firmware version
    version = get_version(ser, address)
    print("Firmware version:", version.strip())

    # Begin cycling the motors at 20% power on/off every second.
    cycle_motors(ser, address, duty_on=2000, delay=1.0)

    ser.close()


if __name__ == "__main__":
    main()
