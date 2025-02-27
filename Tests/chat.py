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
    GETVERSION = 21  # command code for GETVERSION
    ser.reset_input_buffer()
    crc = 0
    # Send address and command
    ser.write(address.to_bytes(1, 'big'))
    crc = crc_update(crc, address)
    ser.write(GETVERSION.to_bytes(1, 'big'))
    crc = crc_update(crc, GETVERSION)

    # Read up to 48 bytes until a null byte is encountered
    version = ""
    for _ in range(48):
        byte = ser.read(1)
        if len(byte) == 0:
            break
        val = byte[0]
        crc = crc_update(crc, val)
        if val == 0:
            break
        version += chr(val)

    # Read the 2-byte checksum from RoboClaw
    checksum_bytes = ser.read(2)
    if len(checksum_bytes) != 2:
        return None
    received_crc = (checksum_bytes[0] << 8) | checksum_bytes[1]
    if crc != received_crc:
        return None  # checksum error
    return version


def get_main_battery(ser, address):
    GETMBATT = 24  # command code for GETMBATT
    ser.reset_input_buffer()
    crc = 0
    ser.write(address.to_bytes(1, 'big'))
    crc = crc_update(crc, address)
    ser.write(GETMBATT.to_bytes(1, 'big'))
    crc = crc_update(crc, GETMBATT)

    # Read 2 bytes (battery voltage)
    data_bytes = ser.read(2)
    if len(data_bytes) != 2:
        return None
    value = (data_bytes[0] << 8) | data_bytes[1]
    crc = crc_update(crc, data_bytes[0])
    crc = crc_update(crc, data_bytes[1])

    # Read 2-byte checksum
    checksum_bytes = ser.read(2)
    if len(checksum_bytes) != 2:
        return None
    received_crc = (checksum_bytes[0] << 8) | checksum_bytes[1]
    if crc != received_crc:
        return None  # checksum error
    return value


def get_eeprom(ser, address, ee_addr):
    READEEPROM = 252  # command code for READ EEPROM
    ser.reset_input_buffer()
    crc = 0
    # Send address, command, and EEPROM address byte
    ser.write(address.to_bytes(1, 'big'))
    crc = crc_update(crc, address)
    ser.write(READEEPROM.to_bytes(1, 'big'))
    crc = crc_update(crc, READEEPROM)
    ser.write(ee_addr.to_bytes(1, 'big'))
    crc = crc_update(crc, ee_addr)

    # Read the 2-byte word stored in EEPROM at ee_addr
    data_bytes = ser.read(2)
    if len(data_bytes) != 2:
        return None
    value = (data_bytes[0] << 8) | data_bytes[1]
    crc = crc_update(crc, data_bytes[0])
    crc = crc_update(crc, data_bytes[1])

    # Read the 2-byte checksum
    checksum_bytes = ser.read(2)
    if len(checksum_bytes) != 2:
        return None
    received_crc = (checksum_bytes[0] << 8) | checksum_bytes[1]
    if crc != received_crc:
        return None  # checksum error
    return value


def print_eeprom_info(ser, address, start=0, count=16):
    print("EEPROM contents:")
    for ee_addr in range(start, start + count):
        value = get_eeprom(ser, address, ee_addr)
        if value is None:
            print(f"  EEPROM[0x{ee_addr:02X}]: Error reading data")
        else:
            # Print the EEPROM word as a hexadecimal value
            print(f"  EEPROM[0x{ee_addr:02X}]: 0x{value:04X}")
        time.sleep(0.01)  # small delay between reads


def main():
    # Use the serial port as requested
    port = '/dev/serial0'  # use '/dev/serial0'
    baudrate = 38400
    address = 0x80         # default RoboClaw address

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return

    time.sleep(0.1)  # Allow time for the port to settle

    version = get_version(ser, address)
    if version is None:
        print("Failed to read firmware version (checksum error or timeout)")
    else:
        print("Firmware Version:", version)

    mbatt = get_main_battery(ser, address)
    if mbatt is None:
        print("Failed to read main battery voltage (checksum error or timeout)")
    else:
        # The raw value may need scaling based on your RoboClaw datasheet
        print("Main Battery Voltage (raw reading):", mbatt)

    print_eeprom_info(ser, address, start=0, count=16)

    ser.close()


if __name__ == '__main__':
    main()
