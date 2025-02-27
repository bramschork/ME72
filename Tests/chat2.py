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
    print("Motor control initialized.")
    print("Enter a speed value between 0 (stop) and 127 (max speed), or 'q' to quit.")

    try:
        while True:
            user_input = input("Enter motor speed (0-127) or 'q' to quit: ")
            if user_input.lower() == 'q':
                break

            try:
                speed = int(user_input)
            except ValueError:
                print("Invalid input. Please enter an integer between 0 and 127.")
                continue

            if speed < 0 or speed > 127:
                print("Speed must be between 0 and 127.")
                continue

            # Send the variable speed to both motors
            left_success = set_motor_duty(ser, address, 1, speed)
            right_success = set_motor_duty(ser, address, 2, speed)
            print(
                f"Set left motor speed to {speed} (success: {left_success}).")
            print(
                f"Set right motor speed to {speed} (success: {right_success}).")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting...")
    finally:
        ser.close()
        print("Serial port closed.")


if __name__ == '__main__':
    main()
