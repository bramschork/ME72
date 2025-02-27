#!/usr/bin/env python3
import serial
import struct
import time


def crc16(data: bytes, init: int = 0) -> int:
    """
    Standard CRC-16/CCITT with given initial value (default 0).
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


def crc16_alt(data: bytes, init: int = 0xFFFF) -> int:
    """
    Alternate CRC-16/CCITT using an initial value of 0xFFFF.
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
    Sends GETVERSION (command 21) and returns the firmware version.
    """
    command = 21
    packet = bytes([address, command])
    # Use standard CRC (init=0)
    crc = crc16(packet, init=0)
    packet += struct.pack('>H', crc)
    ser.write(packet)
    time.sleep(0.1)
    response = ser.read(64)
    return response.decode('ascii', errors='ignore')


def read_battery_voltage(ser: serial.Serial, address: int = 0x80) -> float:
    """
    Reads battery voltage.
    Expected response: [Voltage (2 bytes), Checksum (2 bytes)]
    Prints debug info comparing two CRC variants.
    """
    command = 24
    ser.reset_input_buffer()
    packet = bytes([address, command])
    ser.write(packet)
    time.sleep(0.1)
    response = ser.read(4)
    if len(response) != 4:
        raise Exception("Incomplete response from battery voltage command.")

    # Interpret first 2 bytes as voltage value (big-endian)
    voltage_raw = struct.unpack('>H', response[:2])[0]
    received_crc = struct.unpack('>H', response[2:])[0]
    # Try two different CRC calculations
    calc_crc_0 = crc16(response[:2], init=0)
    calc_crc_ffff = crc16_alt(response[:2], init=0xFFFF)

    print("DEBUG: Battery Voltage Response Bytes:", response.hex())
    print("DEBUG: Voltage Raw Value:", voltage_raw)
    print("DEBUG: Received CRC:", f"{received_crc:04X}")
    print("DEBUG: Calculated CRC (init=0):", f"{calc_crc_0:04X}")
    print("DEBUG: Calculated CRC (init=0xFFFF):", f"{calc_crc_ffff:04X}")

    if received_crc not in (calc_crc_0, calc_crc_ffff):
        raise Exception(f"CRC mismatch in battery voltage: received {received_crc:04X}, "
                        f"calc(init=0) {calc_crc_0:04X}, calc(init=0xFFFF) {calc_crc_ffff:04X}")

    # Convert from tenths of a volt
    voltage = voltage_raw / 10.0
    return voltage


# Mapping for status flags
STATUS_MAP = {
    0x000001: "E-Stop",
    0x000002: "Temperature Error",
    0x000004: "Temperature 2 Error",
    0x000008: "Main Voltage High Error",
    0x000010: "Logic Voltage High Error",
    0x000020: "Logic Voltage Low Error",
    0x000040: "M1 Driver Fault Error",
    0x000080: "M2 Driver Fault Error",
    0x000100: "M1 Speed Error",
    0x000200: "M2 Speed Error",
    0x000400: "M1 Position Error",
    0x000800: "M2 Position Error",
    0x001000: "M1 Current Error",
    0x002000: "M2 Current Error",
    0x010000: "M1 Over Current Warning",
    0x020000: "M2 Over Current Warning",
    0x040000: "Main Voltage High Warning",
    0x080000: "Main Voltage Low Warning",
    0x100000: "Temperature Warning",
    0x200000: "Temperature 2 Warning",
    0x400000: "S4 Signal Triggered",
    0x800000: "S5 Signal Triggered",
    0x01000000: "Speed Error Limit Warning",
    0x02000000: "Position Error Limit Warning"
}


def decode_status(status: int) -> str:
    """
    Decodes a 32-bit status value into human–readable text.
    """
    if status == 0:
        return "Normal"
    names = []
    for bit, name in sorted(STATUS_MAP.items()):
        if status & bit:
            names.append(name)
    return ", ".join(names) if names else "Unknown"


def read_status(ser: serial.Serial, address: int = 0x80) -> int:
    """
    Reads the status.
    Expected response: [Status (4 bytes), Checksum (2 bytes)]
    Prints debug info comparing two CRC variants.
    """
    command = 90
    ser.reset_input_buffer()
    packet = bytes([address, command])
    ser.write(packet)
    time.sleep(0.1)
    response = ser.read(6)
    if len(response) != 6:
        raise Exception("Incomplete response from read status command.")

    status = struct.unpack('>I', response[:4])[0]
    received_crc = struct.unpack('>H', response[4:])[0]
    calc_crc_0 = crc16(response[:4], init=0)
    calc_crc_ffff = crc16_alt(response[:4], init=0xFFFF)

    print("DEBUG: Status Response Bytes:", response.hex())
    print("DEBUG: Status Value:", f"{status:08X}")
    print("DEBUG: Received CRC:", f"{received_crc:04X}")
    print("DEBUG: Calculated CRC (init=0):", f"{calc_crc_0:04X}")
    print("DEBUG: Calculated CRC (init=0xFFFF):", f"{calc_crc_ffff:04X}")

    if received_crc not in (calc_crc_0, calc_crc_ffff):
        raise Exception(f"CRC mismatch in read status: received {received_crc:04X}, "
                        f"calc(init=0) {calc_crc_0:04X}, calc(init=0xFFFF) {calc_crc_ffff:04X}")
    return status


def main():
    port = "/dev/ttyS0"  # Adjust as needed
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
        voltage = read_battery_voltage(ser)
        print(f"Battery Voltage: {voltage:.1f} V")
    except Exception as e:
        print("Error reading battery voltage:", e)

    try:
        status = read_status(ser)
        status_names = decode_status(status)
        print(f"Status: {status:08X} ({status_names})")
    except Exception as e:
        print("Error reading status:", e)

    ser.close()


if __name__ == "__main__":
    main()
