import serial
import time


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def get_version(ser, address):
    GETVERSION = 21  # Command code for GETVERSION
    # Clear any residual data
    ser.reset_input_buffer()
    crc = 0
    # Send address byte
    ser.write(address.to_bytes(1, 'big'))
    crc = crc_update(crc, address)
    # Send GETVERSION command
    ser.write(GETVERSION.to_bytes(1, 'big'))
    crc = crc_update(crc, GETVERSION)

    # Read version string (max 48 bytes, terminated by a 0 byte)
    version = ""
    for i in range(48):
        byte = ser.read(1)
        if len(byte) == 0:
            break  # timeout
        val = byte[0]
        crc = crc_update(crc, val)
        if val == 0:
            break  # end of string
        version += chr(val)

    # Read the two-byte checksum from the RoboClaw
    checksum_bytes = ser.read(2)
    if len(checksum_bytes) != 2:
        return None
    received_crc = (checksum_bytes[0] << 8) | checksum_bytes[1]
    if crc != received_crc:
        return None  # Checksum error
    return version


def get_main_battery(ser, address):
    GETMBATT = 24  # Command code for GETMBATT (main battery voltage)
    ser.reset_input_buffer()
    crc = 0
    # Send address and command bytes
    ser.write(address.to_bytes(1, 'big'))
    crc = crc_update(crc, address)
    ser.write(GETMBATT.to_bytes(1, 'big'))
    crc = crc_update(crc, GETMBATT)

    # Read a two-byte word representing the battery voltage
    data_bytes = ser.read(2)
    if len(data_bytes) != 2:
        return None
    value = (data_bytes[0] << 8) | data_bytes[1]
    crc = crc_update(crc, data_bytes[0])
    crc = crc_update(crc, data_bytes[1])

    # Read the two-byte checksum from the RoboClaw
    checksum_bytes = ser.read(2)
    if len(checksum_bytes) != 2:
        return None
    received_crc = (checksum_bytes[0] << 8) | checksum_bytes[1]
    if crc != received_crc:
        return None  # Checksum error
    return value


def main():
    # Configure these parameters as needed:
    port = '/dev/serial0'   # e.g. 'COM3' for Windows
    baudrate = 38400
    address = 0x80          # Default RoboClaw address

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return

    # Allow time for the serial port to settle
    time.sleep(0.1)

    version = get_version(ser, address)
    if version is None:
        print("Failed to read firmware version (checksum error or timeout)")
    else:
        print("Firmware Version:", version)

    mbatt = get_main_battery(ser, address)
    if mbatt is None:
        print("Failed to read main battery voltage (checksum error or timeout)")
    else:
        # The raw value may need to be scaled (refer to your RoboClaw datasheet)
        print("Main Battery Voltage (raw reading):", mbatt)

    ser.close()


if __name__ == '__main__':
    main()
