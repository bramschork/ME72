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


def writeS2(ser, address, cmd, value, retries=3):
    # This function sends a command with a 16-bit value (using a “writesword” style command)
    for _ in range(retries):
        ser.reset_input_buffer()
        crc = 0
        # Send address
        ser.write(address.to_bytes(1, 'big'))
        crc = crc_update(crc, address)
        # Send command
        ser.write(cmd.to_bytes(1, 'big'))
        crc = crc_update(crc, cmd)
        # Send value as a 2-byte word (big-endian)
        high = (value >> 8) & 0xFF
        low = value & 0xFF
        ser.write(high.to_bytes(1, 'big'))
        crc = crc_update(crc, high)
        ser.write(low.to_bytes(1, 'big'))
        crc = crc_update(crc, low)
        # Send the calculated checksum (2 bytes)
        ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
        ser.write((crc & 0xFF).to_bytes(1, 'big'))
        # Read one acknowledgment byte; nonzero indicates success.
        ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def set_motor_duty(ser, address, motor, duty):
    # For RoboClaw, motor 1 duty command is 32 and motor 2 duty command is 33.
    if motor == 1:
        cmd = 32
    elif motor == 2:
        cmd = 33
    else:
        raise ValueError("Motor must be 1 or 2")
    return writeS2(ser, address, cmd, duty)


def main():
    port = '/dev/serial0'   # Use /dev/serial0 as requested.
    baudrate = 38400
    address = 0x80          # Default RoboClaw address.

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return

    # Allow port to settle
    time.sleep(0.1)

    cycles = 10      # Number of on/off cycles; adjust as needed.
    # Example duty value for "on" (adjust based on your motor specs).
    on_duty = 1000
    off_duty = 0     # Duty value to turn the motor off.

    for i in range(cycles):
        print(f"Cycle {i+1}: Turning motors ON")
        # Set both motors to on_duty
        if not set_motor_duty(ser, address, 1, on_duty):
            print("Failed to set Motor 1 duty")
        if not set_motor_duty(ser, address, 2, on_duty):
            print("Failed to set Motor 2 duty")
        time.sleep(1)  # Motors on for 1 second

        print(f"Cycle {i+1}: Turning motors OFF")
        # Set both motors to off_duty (stopping the motors)
        if not set_motor_duty(ser, address, 1, off_duty):
            print("Failed to set Motor 1 duty")
        if not set_motor_duty(ser, address, 2, off_duty):
            print("Failed to set Motor 2 duty")
        time.sleep(1)  # Motors off for 1 second

    ser.close()


if __name__ == '__main__':
    main()
